import json
import os
from datetime import datetime
from pathlib import Path

import stripe
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from .api_key_manager import validate_api_key


STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY", "")
STRIPE_PRICE_ID = os.getenv("STRIPE_PRICE_ID", "")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
STRIPE_SUCCESS_URL = os.getenv("STRIPE_SUCCESS_URL", f"{FRONTEND_URL}/billing/success")
STRIPE_CANCEL_URL = os.getenv("STRIPE_CANCEL_URL", f"{FRONTEND_URL}/billing/cancel")

if STRIPE_SECRET_KEY:
    stripe.api_key = STRIPE_SECRET_KEY

# In development mode quota checks are skipped entirely so devs can work freely.
DEV_MODE: bool = os.getenv("ENVIRONMENT", "development").lower() == "development"

# Monthly message quotas per subscription status
PLAN_QUOTAS: dict[str, int] = {
    "none": 5000,       # Starter (no subscription)
    "trialing": 50000,  # Free trial
    "active": 50000,    # Pro
    "past_due": 0,      # Blocked until payment resolved
    "canceled": 5000,   # Reverted to Starter
    "unpaid": 0,        # Blocked
}


def _oauth_path() -> Path:
    return Path(__file__).parent / "oauth.json"


def _load_oauth_data(path: Path) -> dict:
    if not path.exists():
        return {"users": []}
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def _save_oauth_data(path: Path, data: dict) -> None:
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)


def _get_authenticated_user(request: Request) -> str | None:
    api_key = request.cookies.get("api_key")
    if not api_key:
        return None
    return validate_api_key(api_key, _oauth_path())


def _get_or_create_customer(user_id: str) -> str:
    oauth_path = _oauth_path()
    data = _load_oauth_data(oauth_path)
    users = data.get("users", [])

    user = next((u for u in users if u.get("user_id") == user_id), None)
    if not user:
        raise ValueError("User not found. Please login first.")

    services = user.setdefault("services", {})
    stripe_service = services.setdefault("stripe", {})
    customer_id = stripe_service.get("customer_id")

    if customer_id:
        return customer_id

    customer = stripe.Customer.create(
        email=user.get("email"),
        metadata={"user_id": user_id},
    )

    stripe_service["customer_id"] = customer["id"]
    stripe_service["connected_at"] = datetime.now().isoformat()
    _save_oauth_data(oauth_path, data)

    return customer["id"]


def _get_user_stripe_data(user_id: str) -> dict:
    """Return the stripe service dict for a user, or empty dict if not found."""
    data = _load_oauth_data(_oauth_path())
    user = next((u for u in data.get("users", []) if u.get("user_id") == user_id), None)
    if not user:
        return {}
    return user.get("services", {}).get("stripe", {})


async def stripe_config(request: Request) -> JSONResponse:
    if not STRIPE_SECRET_KEY:
        return JSONResponse(
            {"error": "Stripe is not configured on the server."},
            status_code=500,
        )

    return JSONResponse(
        {
            "publishable_key": STRIPE_PUBLISHABLE_KEY,
            "default_price_id": STRIPE_PRICE_ID,
            "success_url": STRIPE_SUCCESS_URL,
            "cancel_url": STRIPE_CANCEL_URL,
        }
    )


async def create_checkout_session(request: Request) -> JSONResponse:
    if not STRIPE_SECRET_KEY:
        return JSONResponse(
            {"error": "Stripe is not configured on the server."},
            status_code=500,
        )

    user_id = _get_authenticated_user(request)
    if not user_id:
        return JSONResponse({"error": "Not authenticated."}, status_code=401)

    body = await request.json() if request.headers.get("content-type", "").startswith("application/json") else {}
    price_id = body.get("price_id") or STRIPE_PRICE_ID
    if not price_id:
        return JSONResponse({"error": "Missing Stripe price id."}, status_code=400)

    quantity = int(body.get("quantity", 1))
    mode = body.get("mode", "subscription")
    success_url = body.get("success_url", STRIPE_SUCCESS_URL)
    cancel_url = body.get("cancel_url", STRIPE_CANCEL_URL)

    try:
        customer_id = _get_or_create_customer(user_id)
        session = stripe.checkout.Session.create(
            mode=mode,
            customer=customer_id,
            line_items=[{"price": price_id, "quantity": quantity}],
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={"user_id": user_id, "price_id": price_id},
            **(  # 14-day free trial for new subscriptions
                {"subscription_data": {"trial_period_days": 14}}
                if mode == "subscription"
                else {}
            ),
        )
        return JSONResponse(
            {
                "session_id": session["id"],
                "checkout_url": session.get("url"),
            }
        )
    except ValueError as exc:
        return JSONResponse({"error": str(exc)}, status_code=400)
    except Exception as exc:
        return JSONResponse({"error": f"Stripe checkout failed: {exc}"}, status_code=500)


async def create_billing_portal_session(request: Request) -> JSONResponse:
    if not STRIPE_SECRET_KEY:
        return JSONResponse(
            {"error": "Stripe is not configured on the server."},
            status_code=500,
        )

    user_id = _get_authenticated_user(request)
    if not user_id:
        return JSONResponse({"error": "Not authenticated."}, status_code=401)

    body = await request.json() if request.headers.get("content-type", "").startswith("application/json") else {}
    return_url = body.get("return_url", FRONTEND_URL)

    # Only open portal if the user has an active subscription
    svc = _get_user_stripe_data(user_id)
    if not svc.get("subscription_id"):
        return JSONResponse(
            {"error": "No active subscription found. Please subscribe to a plan first."},
            status_code=400,
        )

    try:
        customer_id = _get_or_create_customer(user_id)
        session = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=return_url,
        )
        return JSONResponse({"portal_url": session["url"]})
    except Exception as exc:
        return JSONResponse({"error": f"Stripe portal failed: {exc}"}, status_code=500)


def _update_subscription_status(
    stripe_customer_id: str,
    status: str,
    subscription_id: str | None,
    price_id: str | None = None,
) -> None:
    """Persist subscription status against the matching user in oauth.json."""
    oauth_path = _oauth_path()
    data = _load_oauth_data(oauth_path)
    for user in data.get("users", []):
        svc = user.get("services", {}).get("stripe", {})
        if svc.get("customer_id") == stripe_customer_id:
            svc["subscription_status"] = status
            if subscription_id:
                svc["subscription_id"] = subscription_id
            if price_id:
                svc["price_id"] = price_id
            svc["updated_at"] = datetime.now().isoformat()
            _save_oauth_data(oauth_path, data)
            print(f"[STRIPE] User {user.get('user_id')} subscription \u2192 {status}")
            return
    print(f"[STRIPE] No user found for customer {stripe_customer_id}")


def get_subscription_status_for_user(user_id: str) -> dict:
    """Public helper for other modules (e.g. app.py) to read a user's subscription state."""
    svc = _get_user_stripe_data(user_id)
    return {
        "status": svc.get("subscription_status", "none"),
        "subscription_id": svc.get("subscription_id"),
        "price_id": svc.get("price_id"),
    }


def check_and_increment_quota(user_id: str) -> tuple[bool, str]:
    """
    Check a user's monthly message quota and increment it if allowed.
    Returns (allowed, reason). Resets counter at the start of each calendar month.
    Quota enforcement is skipped entirely when ENVIRONMENT=development.
    """
    if DEV_MODE:
        return True, ""

    oauth_path = _oauth_path()
    data = _load_oauth_data(oauth_path)
    user = next((u for u in data.get("users", []) if u.get("user_id") == user_id), None)
    if not user:
        return False, "User not found."

    svc = user.setdefault("services", {}).setdefault("stripe", {})
    status = svc.get("subscription_status", "none")
    quota = PLAN_QUOTAS.get(status, 5000)

    if quota == 0:
        return False, "Your payment is past due. Please update your billing information to continue."

    current_month = datetime.now().strftime("%Y-%m")
    if svc.get("quota_month") != current_month:
        svc["quota_month"] = current_month
        svc["messages_this_month"] = 0

    used = svc.get("messages_this_month", 0)
    if used >= quota:
        plan_name = "Pro" if quota > 5000 else "Starter"
        return False, f"Monthly message limit of {quota:,} reached ({plan_name} plan). Upgrade your plan for more."

    svc["messages_this_month"] = used + 1
    _save_oauth_data(oauth_path, data)
    return True, ""


async def get_subscription_status(request: Request) -> JSONResponse:
    user_id = _get_authenticated_user(request)
    if not user_id:
        return JSONResponse({"error": "Not authenticated."}, status_code=401)

    status_data = get_subscription_status_for_user(user_id)
    svc = _get_user_stripe_data(user_id)
    status_data["messages_this_month"] = svc.get("messages_this_month", 0)
    status_data["quota"] = PLAN_QUOTAS.get(status_data["status"], 5000)
    return JSONResponse(status_data)


async def handle_stripe_webhook(request: Request) -> JSONResponse:
    if not STRIPE_SECRET_KEY:
        return JSONResponse(
            {"error": "Stripe is not configured on the server."},
            status_code=500,
        )

    payload = await request.body()
    signature = request.headers.get("Stripe-Signature", "")

    try:
        if STRIPE_WEBHOOK_SECRET:
            event = stripe.Webhook.construct_event(payload=payload, sig_header=signature, secret=STRIPE_WEBHOOK_SECRET)
        else:
            event = json.loads(payload.decode("utf-8"))
    except Exception as exc:
        return JSONResponse({"error": f"Webhook signature validation failed: {exc}"}, status_code=400)

    event_type = event.get("type", "unknown")
    print(f"[STRIPE] Webhook received: {event_type}")

    try:
        if event_type == "checkout.session.completed":
            session_obj = event["data"]["object"]
            customer_id = session_obj.get("customer")
            subscription_id = session_obj.get("subscription")
            price_id_meta = session_obj.get("metadata", {}).get("price_id")
            if customer_id:
                _update_subscription_status(customer_id, "active", subscription_id, price_id_meta)

        elif event_type in ("customer.subscription.updated", "customer.subscription.deleted"):
            sub = event["data"]["object"]
            customer_id = sub.get("customer")
            status = sub.get("status", "canceled")
            if customer_id:
                _update_subscription_status(customer_id, status, sub.get("id"))

        elif event_type == "invoice.payment_failed":
            invoice = event["data"]["object"]
            customer_id = invoice.get("customer")
            if customer_id:
                _update_subscription_status(customer_id, "past_due", invoice.get("subscription"))
    except Exception as exc:
        print(f"[STRIPE] Webhook handler error: {exc}")

    return JSONResponse({"received": True, "event_type": event_type})


stripe_app = Starlette(
    routes=[
        Route("/config", stripe_config, methods=["GET"]),
        Route("/subscription/status", get_subscription_status, methods=["GET"]),
        Route("/checkout/session", create_checkout_session, methods=["POST"]),
        Route("/billing-portal/session", create_billing_portal_session, methods=["POST"]),
        Route("/webhook", handle_stripe_webhook, methods=["POST"]),
    ]
)
