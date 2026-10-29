"""JWT and JWKS token verification adhering to strict zero-trust identity standards."""

import logging
import time
from typing import Any, Dict, List, Optional
from fastapi import HTTPException, status
import jwt
from jwt.exceptions import (
    ExpiredSignatureError,
    ImmatureSignatureError,
    InvalidAudienceError,
    InvalidIssuerError,
    InvalidSignatureError,
    InvalidTokenError,
    PyJWTError,
)

logger = logging.getLogger(__name__)


class JWKSVerificationError(HTTPException):
    """Specific HTTP 401 exception for JWT/JWKS verification failures."""

    def __init__(self, detail: str, error_type: str = "invalid_token"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": f'Bearer error="{error_type}", error_description="{detail}"'},
        )


class JWKSTokenVerifier:
    """Production-grade JWKS and asymmetric JWT token verifier."""

    def __init__(
        self,
        issuer: Optional[str] = None,
        audience: Optional[str] = None,
        jwks_url: Optional[str] = None,
        algorithms: Optional[List[str]] = None,
        required_claims: Optional[List[str]] = None,
        clock_skew_seconds: int = 60,
        jwks_cache_ttl_seconds: int = 300,
        min_refresh_interval_seconds: float = 2.0,
        static_keys: Optional[Dict[str, Any]] = None,
    ):
        self.issuer = issuer
        self.audience = audience
        self.jwks_url = jwks_url
        self.algorithms = [alg for alg in (algorithms or ["RS256"]) if alg.lower() != "none"]
        if not self.algorithms:
            raise ValueError("At least one asymmetric algorithm (e.g. RS256) must be allowed; 'none' is forbidden.")

        self.required_claims = required_claims or ["sub"]
        self.clock_skew_seconds = max(0, clock_skew_seconds)
        self.jwks_cache_ttl_seconds = max(10, jwks_cache_ttl_seconds)
        self.min_refresh_interval_seconds = max(0.5, min_refresh_interval_seconds)

        # In-memory JWKS cache: kid -> public_key (PEM or cryptography RSAPublicKey)
        self._key_cache: Dict[str, Any] = {}
        self._cache_timestamp: float = 0.0
        self._last_refresh_timestamp: float = 0.0

        # Optional static/preloaded keys (e.g. for testing)
        if static_keys:
            self._key_cache.update(static_keys)
            self._cache_timestamp = time.time()

    def set_static_keys(self, keys: Dict[str, Any]) -> None:
        """Inject or rotate public keys directly (used primarily in test suites)."""
        self._key_cache = dict(keys)
        self._cache_timestamp = time.time()

    def _fetch_jwks_keys(self) -> Dict[str, Any]:
        """Fetch JWKS public keys from the configured remote endpoint."""
        if not self.jwks_url:
            return {}

        import httpx

        try:
            with httpx.Client(timeout=5.0) as client:
                response = client.get(self.jwks_url)
                response.raise_for_status()
                data = response.json()
        except Exception as exc:
            logger.error(f"Failed to fetch JWKS from {self.jwks_url}: {exc}")
            raise JWKSVerificationError(
                detail="Identity provider JWKS endpoint is unreachable.",
                error_type="temporarily_unavailable",
            )

        keys_by_kid = {}
        for key_dict in data.get("keys", []):
            kid = key_dict.get("kid")
            if not kid:
                continue
            try:
                public_key = jwt.algorithms.RSAAlgorithm.from_jwk(key_dict)
                keys_by_kid[kid] = public_key
            except Exception as exc:
                logger.warning(f"Could not parse JWK with kid '{kid}': {exc}")
        return keys_by_kid

    def get_signing_key(self, kid: Optional[str]) -> Any:
        """Resolve public signing key for the given kid with TTL and refresh rate-limiting."""
        now = time.time()

        # Check cache validity
        cache_valid = (now - self._cache_timestamp) < self.jwks_cache_ttl_seconds

        # 1. Check if key is already cached and cache is fresh
        if kid and kid in self._key_cache and cache_valid:
            return self._key_cache[kid]

        # 2. If kid is missing or cache expired or unknown kid encountered
        # Apply rate limiting on refresh to protect against unknown kid DoS attacks
        if (now - self._last_refresh_timestamp) >= self.min_refresh_interval_seconds:
            self._last_refresh_timestamp = now
            if self.jwks_url:
                try:
                    fetched_keys = self._fetch_jwks_keys()
                    self._key_cache.update(fetched_keys)
                    self._cache_timestamp = now
                except JWKSVerificationError:
                    # If fetch fails but we already have the requested key in cache (even if stale), keep using it
                    if kid and kid in self._key_cache:
                        return self._key_cache[kid]
                    raise

        # 3. Lookup after refresh
        if kid:
            if kid in self._key_cache:
                return self._key_cache[kid]
            raise JWKSVerificationError(
                detail=f"Key ID (kid) '{kid}' not found in trusted JWKS key set.",
                error_type="invalid_token",
            )

        # If token has no kid header, allow single registered key if exactly 1 key is known
        if len(self._key_cache) == 1:
            return next(iter(self._key_cache.values()))

        raise JWKSVerificationError(
            detail="Token header missing 'kid' and multiple keys exist in key set.",
            error_type="invalid_token",
        )

    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify JWT signature, algorithm, issuer, audience, and temporal validity."""
        if not token or not token.strip():
            raise JWKSVerificationError(detail="Missing bearer authentication token.")

        raw_token = token.strip()

        # Extract unverified header to inspect kid and alg
        try:
            unverified_header = jwt.get_unverified_header(raw_token)
        except PyJWTError as exc:
            logger.warning(f"Malformed JWT header: {exc}")
            raise JWKSVerificationError(detail="Malformed JWT token header.")

        alg = unverified_header.get("alg")
        if not alg or alg.lower() == "none" or alg not in self.algorithms:
            logger.warning(f"Rejected token with disallowed or missing algorithm: {alg}")
            raise JWKSVerificationError(
                detail=f"Disallowed or unsupported token signing algorithm '{alg}'.",
                error_type="invalid_token",
            )

        kid = unverified_header.get("kid")
        signing_key = self.get_signing_key(kid)

        # Decode options and claims validation
        decode_kwargs: Dict[str, Any] = {
            "algorithms": self.algorithms,
            "leeway": self.clock_skew_seconds,
            "options": {
                "verify_signature": True,
                "verify_exp": True,
                "verify_nbf": True,
                "verify_iat": True,
                "verify_aud": self.audience is not None,
                "verify_iss": self.issuer is not None,
                "require": self.required_claims,
            },
        }

        if self.issuer:
            decode_kwargs["issuer"] = self.issuer
        if self.audience:
            decode_kwargs["audience"] = self.audience

        try:
            payload = jwt.decode(raw_token, signing_key, **decode_kwargs)
        except ExpiredSignatureError:
            raise JWKSVerificationError(detail="Token has expired.", error_type="invalid_token")
        except ImmatureSignatureError:
            raise JWKSVerificationError(detail="Token not yet valid (nbf in future).", error_type="invalid_token")
        except InvalidIssuerError:
            raise JWKSVerificationError(detail="Token issuer (iss) mismatch.", error_type="invalid_token")
        except InvalidAudienceError:
            raise JWKSVerificationError(detail="Token audience (aud) mismatch.", error_type="invalid_token")
        except InvalidSignatureError:
            raise JWKSVerificationError(detail="Cryptographic token signature verification failed.", error_type="invalid_token")
        except InvalidTokenError as exc:
            raise JWKSVerificationError(detail=f"Invalid token: {exc}", error_type="invalid_token")
        except Exception as exc:
            logger.error(f"Unexpected error during token verification: {exc}")
            raise JWKSVerificationError(detail="Authentication token verification failed.", error_type="invalid_token")

        # Strictly enforce non-empty sub
        sub = payload.get("sub")
        if not sub or not str(sub).strip():
            raise JWKSVerificationError(detail="Token missing authoritative subject ('sub') claim.")

        return payload

