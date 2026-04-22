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
            metadata={"user_id": user_id},
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

    try:
        customer_id = _get_or_create_customer(user_id)
        session = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=return_url,
        )
        return JSONResponse({"portal_url": session["url"]})
    except Exception as exc:
        return JSONResponse({"error": f"Stripe portal failed: {exc}"}, status_code=500)


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

    return JSONResponse({"received": True, "event_type": event_type})


stripe_app = Starlette(
    routes=[
        Route("/config", stripe_config, methods=["GET"]),
        Route("/checkout/session", create_checkout_session, methods=["POST"]),
        Route("/billing-portal/session", create_billing_portal_session, methods=["POST"]),
        Route("/webhook", handle_stripe_webhook, methods=["POST"]),
    ]
)
