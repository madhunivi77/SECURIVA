"""
Telesign Token Management API Endpoints

Provides REST API for managing Telesign OAuth tokens
"""

from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import JSONResponse
from starlette.requests import Request
from pathlib import Path
import json

from .telesign_token_manager import get_token_manager
from .api_key_manager import validate_api_key


async def api_telesign_token_store(request: Request):
    """
    Store a new Telesign OAuth token
    
    POST /telesign/token/store
    Body: {
        "customer_id": "xxx",
        "access_token": "xxx",
        "refresh_token": "xxx",
        "expires_in": 3600
    }
    """
    # Authenticate
    api_key = request.cookies.get("api_key")
    if not api_key:
        return JSONResponse(
            {"error": "Not authenticated"},
            status_code=401
        )
    
    oauth_file = Path(__file__).parent / "oauth.json"
    user_id = validate_api_key(api_key, oauth_file)
    
    if not user_id:
        return JSONResponse(
            {"error": "Invalid API key"},
            status_code=401
        )
    
    try:
        data = await request.json()
        
        # Validate required fields
        required_fields = ['customer_id', 'access_token']
        if not all(field in data for field in required_fields):
            return JSONResponse(
                {"error": f"Missing required fields: {required_fields}"},
                status_code=400
            )
        
        # Store token
        token_manager = get_token_manager()
        token = token_manager.store_token(
            customer_id=data['customer_id'],
            access_token=data['access_token'],
            refresh_token=data.get('refresh_token'),
            expires_in=data.get('expires_in', 3600),
            token_type=data.get('token_type', 'Bearer'),
            scope=data.get('scope', 'whatsapp')
        )
        
        return JSONResponse({
            "status": "success",
            "message": "Token stored successfully",
            "customer_id": token.customer_id,
            "expires_at": token.expires_at
        })
        
    except Exception as e:
        return JSONResponse(
            {"error": str(e)},
            status_code=500
        )


async def api_telesign_token_get(request: Request):
    """
    Get current token status
    
    GET /telesign/token/{customer_id}
    """
    # Authenticate
    api_key = request.cookies.get("api_key")
    if not api_key:
        return JSONResponse(
            {"error": "Not authenticated"},
            status_code=401
        )
    
    oauth_file = Path(__file__).parent / "oauth.json"
    user_id = validate_api_key(api_key, oauth_file)
    
    if not user_id:
        return JSONResponse(
            {"error": "Invalid API key"},
            status_code=401
        )
    
    try:
        customer_id = request.path_params.get('customer_id')
        
        token_manager = get_token_manager()
        token = token_manager.get_token(customer_id)
        
        if not token:
            return JSONResponse(
                {"error": "Token not found"},
                status_code=404
            )
        
        return JSONResponse({
            "customer_id": token.customer_id,
            "token_type": token.token_type,
            "scope": token.scope,
            "expires_at": token.expires_at,
            "has_refresh_token": token.refresh_token is not None,
            "refresh_count": token.refresh_count
        })
        
    except Exception as e:
        return JSONResponse(
            {"error": str(e)},
            status_code=500
        )


async def api_telesign_token_refresh(request: Request):
    """
    Manually refresh a token
    
    POST /telesign/token/{customer_id}/refresh
    """
    # Authenticate
    api_key = request.cookies.get("api_key")
    if not api_key:
        return JSONResponse(
            {"error": "Not authenticated"},
            status_code=401
        )
    
    oauth_file = Path(__file__).parent / "oauth.json"
    user_id = validate_api_key(api_key, oauth_file)
    
    if not user_id:
        return JSONResponse(
            {"error": "Invalid API key"},
            status_code=401
        )
    
    try:
        customer_id = request.path_params.get('customer_id')
        
        token_manager = get_token_manager()
        token = token_manager.refresh_token(customer_id)
        
        if not token:
            return JSONResponse(
                {"error": "Token refresh failed"},
                status_code=500
            )
        
        return JSONResponse({
            "status": "success",
            "message": "Token refreshed successfully",
            "customer_id": token.customer_id,
            "expires_at": token.expires_at,
            "refresh_count": token.refresh_count
        })
        
    except Exception as e:
        return JSONResponse(
            {"error": str(e)},
            status_code=500
        )


async def api_telesign_token_list(request: Request):
    """
    List all stored tokens
    
    GET /telesign/token/list
    """
    # Authenticate
    api_key = request.cookies.get("api_key")
    if not api_key:
        return JSONResponse(
            {"error": "Not authenticated"},
            status_code=401
        )
    
    oauth_file = Path(__file__).parent / "oauth.json"
    user_id = validate_api_key(api_key, oauth_file)
    
    if not user_id:
        return JSONResponse(
            {"error": "Invalid API key"},
            status_code=401
        )
    
    try:
        token_manager = get_token_manager()
        tokens = token_manager.list_tokens()
        
        return JSONResponse({
            "status": "success",
            "count": len(tokens),
            "tokens": tokens
        })
        
    except Exception as e:
        return JSONResponse(
            {"error": str(e)},
            status_code=500
        )


async def api_telesign_token_revoke(request: Request):
    """
    Revoke a token
    
    DELETE /telesign/token/{customer_id}
    """
    # Authenticate
    api_key = request.cookies.get("api_key")
    if not api_key:
        return JSONResponse(
            {"error": "Not authenticated"},
            status_code=401
        )
    
    oauth_file = Path(__file__).parent / "oauth.json"
    user_id = validate_api_key(api_key, oauth_file)
    
    if not user_id:
        return JSONResponse(
            {"error": "Invalid API key"},
            status_code=401
        )
    
    try:
        customer_id = request.path_params.get('customer_id')
        
        token_manager = get_token_manager()
        success = token_manager.revoke_token(customer_id)
        
        if not success:
            return JSONResponse(
                {"error": "Token not found"},
                status_code=404
            )
        
        return JSONResponse({
            "status": "success",
            "message": "Token revoked successfully"
        })
        
    except Exception as e:
        return JSONResponse(
            {"error": str(e)},
            status_code=500
        )


# Starlette app for token management
telesign_token_routes = [
    Route("/token/store", api_telesign_token_store, methods=["POST"]),
    Route("/token/{customer_id}", api_telesign_token_get, methods=["GET"]),
    Route("/token/{customer_id}/refresh", api_telesign_token_refresh, methods=["POST"]),
    Route("/token/list", api_telesign_token_list, methods=["GET"]),
    Route("/token/{customer_id}", api_telesign_token_revoke, methods=["DELETE"]),
]

telesign_token_app = Starlette(routes=telesign_token_routes)