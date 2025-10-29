"""
Centralized Configuration for SECURIVA Backend

All environment variables, constants, and configuration values are defined here.
This provides a single source of truth for the entire application.
"""

import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # ============================================================================
    # ENVIRONMENT
    # ============================================================================
    ENVIRONMENT: str = Field(default="development", description="Environment: development, staging, production")

    # ============================================================================
    # SERVER URLS
    # ============================================================================
    BACKEND_URL: str = Field(default="http://localhost:8000", description="Backend server URL")
    FRONTEND_URL: str = Field(default="http://localhost:5173", description="Frontend application URL")
    MCP_SERVER_URL: str = Field(default="http://localhost:8000/mcp/", description="MCP server endpoint URL")
    AUTH_SERVER_URL: str = Field(default="http://localhost:8000/auth/token", description="Auth server token endpoint")

    # ============================================================================
    # SECURITY & JWT
    # ============================================================================
    JWT_SECRET_KEY: str = Field(..., description="Secret key for JWT signing (REQUIRED)")
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT signing algorithm")
    JWT_EXPIRATION_HOURS: int = Field(default=1, description="JWT token expiration in hours")

    # ============================================================================
    # COOKIES
    # ============================================================================
    COOKIE_SAMESITE: str = Field(default="lax", description="Cookie SameSite attribute: lax, strict, none")
    COOKIE_SECURE: bool = Field(default=False, description="Use secure cookies (HTTPS only)")
    SESSION_COOKIE_MAX_AGE: int = Field(default=30 * 24 * 3600, description="Session cookie max age in seconds (default 30 days)")
    AUTH_COOKIE_MAX_AGE: int = Field(default=3600, description="Auth token cookie max age in seconds (default 1 hour)")

    @property
    def cookie_secure_computed(self) -> bool:
        """
        Compute cookie secure flag based on environment and settings.

        In development with SameSite=None, we can use Secure=False (Chrome allows this for localhost).
        In production, SameSite=None REQUIRES Secure=True.
        """
        if self.COOKIE_SAMESITE.lower() == "none":
            return self.ENVIRONMENT == "production"
        return self.ENVIRONMENT == "production" or self.COOKIE_SECURE

    # ============================================================================
    # GOOGLE OAUTH
    # ============================================================================
    GOOGLE_CLIENT_ID: str = Field(..., description="Google OAuth Client ID (REQUIRED)")
    GOOGLE_CLIENT_SECRET: str = Field(..., description="Google OAuth Client Secret (REQUIRED)")

    @property
    def GOOGLE_REDIRECT_URI(self) -> str:
        """Dynamic redirect URI based on backend URL."""
        return f"{self.BACKEND_URL}/callback"

    # GOOGLE_SCOPES: List[str] = Field(
    #     default=[
    #         "openid",
    #         "https://www.googleapis.com/auth/gmail.readonly",
    #         "https://www.googleapis.com/auth/calendar.readonly",
    #         "https://www.googleapis.com/auth/userinfo.profile",
    #         "https://www.googleapis.com/auth/userinfo.email",
    #     ],
    #     description="Google OAuth scopes"
    # )

    # OAuth configuration for google-auth-oauthlib
    @property
    def GOOGLE_OAUTH_CONFIG(self) -> dict:
        """Complete Google OAuth configuration dictionary."""
        return {
            "web": {
                "client_id": self.GOOGLE_CLIENT_ID,
                "client_secret": self.GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        }

    # ============================================================================
    # LLM PROVIDERS
    # ============================================================================
    OPENAI_API_KEY: str = Field(..., description="OpenAI API key (REQUIRED)")
    GROQ_API_KEY: str = Field(default="", description="Groq API key (optional)")

    DEFAULT_LLM_API: str = Field(default="openai", description="Default LLM provider: openai or groq")
    DEFAULT_LLM_MODEL: str = Field(default="gpt-3.5-turbo", description="Default LLM model")

    # ============================================================================
    # SESSION STORAGE
    # ============================================================================
    SESSION_CACHE_TTL: int = Field(default=600, description="Session cache TTL in seconds (default 10 minutes)")
    SESSION_MAX_CACHE_SIZE: int = Field(default=1000, description="Maximum number of sessions to cache")
    SESSION_CLEANUP_MAX_AGE_DAYS: int = Field(default=30, description="Delete sessions older than N days")

    # ============================================================================
    # CORS
    # ============================================================================
    @property
    def CORS_ORIGINS(self) -> List[str]:
        """Allowed CORS origins."""
        return [self.FRONTEND_URL]

    # ============================================================================
    # LOGGING
    # ============================================================================
    LOG_LEVEL: str = Field(default="INFO", description="Logging level: DEBUG, INFO, WARNING, ERROR")

    # ============================================================================
    # PYDANTIC SETTINGS CONFIGURATION
    # ============================================================================
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"  # Ignore extra environment variables


# ============================================================================
# GLOBAL SETTINGS INSTANCE
# ============================================================================
settings = Settings()


# ============================================================================
# OAUTH INSECURE TRANSPORT (Development Only)
# ============================================================================
if settings.ENVIRONMENT == "development":
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
