"""Composio connection management endpoints.

- GET /api/composio/connections  → list user's connected third-party accounts
- POST /api/composio/connect      → initiate OAuth for a toolkit, return redirect URL
"""

import asyncio
import json
import os
import traceback
from pathlib import Path

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from .api_key_manager import validate_api_key

_composio_client = None
_composio_error: str | None = None

if os.getenv("COMPOSIO_API_KEY"):
    try:
        from composio import Composio
        _composio_client = Composio()
    except Exception as e:
        _composio_error = f"{type(e).__name__}: {e}"


def _get_user_id(request: Request) -> str | None:
    api_key = request.cookies.get("api_key")
    if not api_key:
        return None
    oauth_file = Path(__file__).parent / "oauth.json"
    return validate_api_key(api_key, oauth_file)


def _require_composio() -> JSONResponse | None:
    if _composio_client is None:
        return JSONResponse(
            {"error": "Composio not configured", "detail": _composio_error},
            status_code=503,
        )
    return None


async def list_toolkits(request: Request):
    """List available Composio toolkits (apps the user can potentially connect).
    Query params: limit (default 200), category (optional), sort_by (optional).
    """
    guard = _require_composio()
    if guard is not None:
        return guard

    try:
        limit = int(request.query_params.get("limit", "200"))
    except ValueError:
        limit = 200
    category = request.query_params.get("category")
    sort_by = request.query_params.get("sort_by", "usage")

    try:
        kwargs = {"limit": limit, "sort_by": sort_by}
        if category:
            kwargs["category"] = category
        res = await asyncio.to_thread(_composio_client.toolkits.list, **kwargs)
        items = []
        for item in getattr(res, "items", []) or []:
            if getattr(item, "deprecated", None) and getattr(item.deprecated, "toolkit_id", None):
                # Include but mark deprecated - caller decides
                pass
            meta = getattr(item, "meta", None)
            description = getattr(meta, "description", "") if meta else ""
            logo = getattr(meta, "logo", None) if meta else None
            categories = []
            if meta and getattr(meta, "categories", None):
                categories = [getattr(c, "name", None) or getattr(c, "id", None) for c in meta.categories]
            tools_count = getattr(meta, "tools_count", None) if meta else None
            auth_schemes = getattr(item, "auth_schemes", []) or []
            items.append(
                {
                    "name": getattr(item, "name", None),
                    "slug": getattr(item, "slug", None),
                    "description": description,
                    "logo": logo,
                    "categories": categories,
                    "tools_count": tools_count,
                    "auth_schemes": auth_schemes,
                    "no_auth": bool(getattr(item, "no_auth", False)),
                }
            )
        return JSONResponse(
            {
                "toolkits": items,
                "total_items": getattr(res, "total_items", None),
                "next_cursor": getattr(res, "next_cursor", None),
            }
        )
    except Exception as e:
        return JSONResponse(
            {"error": str(e), "traceback": traceback.format_exc()},
            status_code=500,
        )


async def list_connections(request: Request):
    user_id = _get_user_id(request)
    if not user_id:
        return JSONResponse({"error": "Not authenticated"}, status_code=401)

    guard = _require_composio()
    if guard is not None:
        return guard

    try:
        res = await asyncio.to_thread(
            _composio_client.connected_accounts.list, user_ids=[user_id]
        )
        items = []
        for item in getattr(res, "items", []) or []:
            toolkit = getattr(item, "toolkit", None)
            slug = getattr(toolkit, "slug", None) if toolkit else None
            items.append(
                {
                    "id": getattr(item, "id", None),
                    "toolkit": slug,
                    "status": getattr(item, "status", None),
                }
            )
        return JSONResponse({"connections": items})
    except Exception as e:
        return JSONResponse(
            {"error": str(e), "traceback": traceback.format_exc()},
            status_code=500,
        )


async def initiate_connection(request: Request):
    user_id = _get_user_id(request)
    if not user_id:
        return JSONResponse({"error": "Not authenticated"}, status_code=401)

    guard = _require_composio()
    if guard is not None:
        return guard

    try:
        body = await request.json()
    except json.JSONDecodeError:
        return JSONResponse({"error": "Invalid JSON body"}, status_code=400)

    toolkit = body.get("toolkit")
    if not toolkit or not isinstance(toolkit, str):
        return JSONResponse({"error": "Missing or invalid 'toolkit'"}, status_code=400)

    try:
        # Use session.authorize (tool-router scoped) instead of top-level
        # toolkits.authorize, so the connection is bound to the same
        # auth_config the MCP tool-router uses — otherwise the agent
        # can't see it even though it shows as ACTIVE in connected_accounts.list.
        session = await asyncio.to_thread(_composio_client.create, user_id=user_id)
        req_obj = await asyncio.to_thread(session.authorize, toolkit)
        return JSONResponse(
            {
                "toolkit": toolkit,
                "redirect_url": getattr(req_obj, "redirect_url", None),
                "connection_id": getattr(req_obj, "id", None),
                "status": getattr(req_obj, "status", None),
            }
        )
    except Exception as e:
        return JSONResponse(
            {"error": str(e), "traceback": traceback.format_exc()},
            status_code=500,
        )


composio_app = Starlette(
    routes=[
        Route("/toolkits", list_toolkits, methods=["GET"]),
        Route("/connections", list_connections, methods=["GET"]),
        Route("/connect", initiate_connection, methods=["POST"]),
    ]
)
