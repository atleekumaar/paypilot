"""Authentication and user identity resolution enforcing zero-trust client ownership and cryptographic JWT/JWKS verification."""

import logging
from typing import Any, Dict, Optional
from fastapi import Header, HTTPException, Request, status
from pydantic import BaseModel, Field

from app.core.config import get_settings
from app.core.jwt_auth import JWKSTokenVerifier, JWKSVerificationError

logger = logging.getLogger(__name__)

# Global singleton or test-overridable verifier instance
_jwt_verifier: Optional[JWKSTokenVerifier] = None


def get_jwt_verifier() -> JWKSTokenVerifier:
    """Return configured JWKSTokenVerifier instance."""
    global _jwt_verifier
    if _jwt_verifier is None:
        settings = get_settings()
        _jwt_verifier = JWKSTokenVerifier(
            issuer=settings.AUTH_ISSUER,
            audience=settings.AUTH_AUDIENCE,
            jwks_url=settings.AUTH_JWKS_URL,
            algorithms=settings.AUTH_ALGORITHMS,
            required_claims=settings.AUTH_REQUIRED_CLAIMS,
            clock_skew_seconds=settings.AUTH_CLOCK_SKEW_SECONDS,
        )
    return _jwt_verifier


def set_jwt_verifier(verifier: Optional[JWKSTokenVerifier]) -> None:
    """Override or reset the global JWT verifier (for testing)."""
    global _jwt_verifier
    _jwt_verifier = verifier


class AuthenticatedUser(BaseModel):
    """Authenticated user context derived authoritatively by backend."""

    id: str = Field(..., description="Unique authenticated user ID")
    username: Optional[str] = Field(default=None, description="Display name")
    is_authenticated: bool = Field(default=True, description="Whether identity has been verified")
    email: Optional[str] = Field(default=None, description="User email if available in claims")
    claims: Optional[Dict[str, Any]] = Field(default=None, description="Verified claims payload")


def get_current_user(
    request: Request,
    authorization: Optional[str] = Header(default=None),
    x_user_id: Optional[str] = Header(default=None, alias="X-User-Id"),
) -> AuthenticatedUser:
    """Resolve authenticated user identity from trusted request credentials.

    Critical Security Rules:
    1. Client-provided query parameters or request body properties (e.g. `?user_id=...`)
       are NEVER trusted as proof of identity.
    2. When AUTH_MODE == "jwt" (mandatory in production):
       - Authorization: Bearer <JWT> is mandatory.
       - The token is verified cryptographically via asymmetric JWKS public keys.
       - Client-provided headers (including X-User-Id) are completely ignored.
       - Missing, invalid, expired, or unverified tokens immediately return HTTP 401.
    3. When AUTH_MODE == "demo":
       - Allowed ONLY when ENVIRONMENT != "production".
       - In production, demo mode is rejected fail-closed.
       - For local development and demo testing, permits Bearer or X-User-Id headers,
         falling back to 'guest_user' if absent.
    """
    settings = get_settings()
    auth_mode = settings.AUTH_MODE.lower()
    is_production = settings.ENVIRONMENT.lower() == "production"

    # Enforce fail-closed check in production
    if is_production and auth_mode != "jwt":
        logger.critical("Security misconfiguration: Demo authentication attempted in production environment!")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server authentication configuration error: Demo mode is forbidden in production.",
        )

    # -------------------------------------------------------------
    # Production / JWT Authentication Mode
    # -------------------------------------------------------------
    if auth_mode == "jwt":
        if not authorization or not authorization.startswith("Bearer "):
            raise JWKSVerificationError(
                detail="Missing Bearer authorization header.",
                error_type="invalid_token",
            )

        token = authorization[7:].strip()
        if not token:
            raise JWKSVerificationError(
                detail="Empty Bearer authorization token.",
                error_type="invalid_token",
            )

        verifier = get_jwt_verifier()
        claims = verifier.verify_token(token)

        user_id = str(claims["sub"])
        username = (
            claims.get("preferred_username")
            or claims.get("name")
            or claims.get("email")
            or f"User {user_id[:8] if len(user_id) > 8 else user_id}"
        )
        email = claims.get("email")

        return AuthenticatedUser(
            id=user_id,
            username=username,
            email=email,
            is_authenticated=True,
            claims=claims,
        )

    # -------------------------------------------------------------
    # Local Demo Authentication Mode (Non-Production Only)
    # -------------------------------------------------------------
    user_id: Optional[str] = None

    # 1. Authorization: Bearer <token_or_userid>
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:].strip()
        if token:
            user_id = token
            if user_id.startswith("token_"):
                user_id = user_id[6:]

    # 2. X-User-Id header (trusted API Gateway or demo header)
    elif x_user_id and x_user_id.strip():
        user_id = x_user_id.strip()

    # 3. Default fallback for anonymous / guest sessions
    if not user_id:
        user_id = "guest_user"

    return AuthenticatedUser(
        id=user_id,
        username=f"User {user_id}",
        is_authenticated=True,
    )


def verify_user_ownership(authenticated_user: AuthenticatedUser, client_user_id: Optional[str]) -> None:
    """Ensure client cannot spoof another user's identity via untrusted parameters.

    If a client explicitly submits a user_id that differs from their authenticated identity,
    the request is strictly rejected with HTTP 403 Forbidden.
    """
    if client_user_id is not None and client_user_id.strip() and client_user_id.strip() != authenticated_user.id:
        logger.warning(
            f"Security violation: Authenticated user '{authenticated_user.id}' attempted to act as '{client_user_id}'"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied: Client-provided user_id '{client_user_id}' does not match authenticated identity '{authenticated_user.id}'.",
        )
