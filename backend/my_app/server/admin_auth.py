import os
from datetime import datetime, timedelta

from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from pydantic import BaseModel

load_dotenv()

router = APIRouter()
security = HTTPBearer()

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
ADMIN_SECRET_KEY = os.getenv("ADMIN_SECRET_KEY")

ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = 2


class AdminLoginRequest(BaseModel):
    email: str
    password: str


def create_admin_token(email: str):
    expire = datetime.utcnow() + timedelta(hours=TOKEN_EXPIRE_HOURS)

    payload = {
        "sub": email,
        "role": "admin",
        "exp": expire,
    }

    return jwt.encode(payload, ADMIN_SECRET_KEY, algorithm=ALGORITHM)


@router.post("/admin/login")
def admin_login(data: AdminLoginRequest):
    if not ADMIN_EMAIL or not ADMIN_PASSWORD or not ADMIN_SECRET_KEY:
        raise HTTPException(status_code=500, detail="Admin auth environment variables are missing")

    if data.email == ADMIN_EMAIL and data.password == ADMIN_PASSWORD:
        token = create_admin_token(data.email)
        return {
            "access_token": token,
            "token_type": "bearer",
            "role": "admin",
        }

    raise HTTPException(status_code=401, detail="Invalid admin credentials")


def require_admin(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, ADMIN_SECRET_KEY, algorithms=[ALGORITHM])

        if payload.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")

        return payload

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


@router.get("/admin/verify")
def verify_admin(admin=Depends(require_admin)):
    return {
        "ok": True,
        "email": admin.get("sub"),
        "role": admin.get("role"),
    }