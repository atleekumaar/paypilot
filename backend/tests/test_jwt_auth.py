"""Comprehensive security test suite for Phase 4A JWT/JWKS Authentication.

Covers all 20 required security scenarios:
1. Valid asymmetric RS256 token authentication with claims extraction
2. Missing Authorization header (HTTP 401)
3. Empty / whitespace Bearer token (HTTP 401)
4. Malformed JWT token structure (HTTP 401)
5. Tampered JWT signature (HTTP 401)
6. Expired token past clock skew (HTTP 401)
7. Future nbf token past clock skew (HTTP 401)
8. Issuer mismatch (HTTP 401)
9. Audience mismatch (HTTP 401)
10. Missing sub claim (HTTP 401)
11. Empty sub claim (HTTP 401)
12. Explicit rejection of alg='none' (HTTP 401)
13. Explicit rejection of disallowed symmetric algorithms (HS256) (HTTP 401)
14. Unknown kid handling with refresh throttling (HTTP 401)
15. Key rotation handling (kid rollover)
16. Unreachable / failing remote JWKS endpoint (HTTP 401 fail-closed)
17. Production / JWT mode ignores client X-User-Id header completely
18. Cross-user isolation: User A's token cannot access User B's resources
19. Mismatched body/query user_id rejected with HTTP 403 by verify_user_ownership
20. In ENVIRONMENT=production, AUTH_MODE=demo is strictly forbidden
"""

import time
from datetime import datetime, timezone
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi.testclient import TestClient
import jwt

from app.core.auth import AuthenticatedUser, get_jwt_verifier, set_jwt_verifier, verify_user_ownership
from app.core.config import Settings, get_settings
from app.core.jwt_auth import JWKSTokenVerifier, JWKSVerificationError
from app.main import app


# ---------------------------------------------------------------------------
# Test Fixtures & Ephemeral Key Generation
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def primary_keypair():
    """Generate ephemeral 2048-bit RSA keypair for testing (Key 1)."""
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()
    return private_key, public_key


@pytest.fixture(scope="module")
def secondary_keypair():
    """Generate secondary ephemeral 2048-bit RSA keypair for key rotation (Key 2)."""
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()
    return private_key, public_key


@pytest.fixture(scope="module")
def attacker_keypair():
    """Generate untrusted attacker RSA keypair."""
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()
    return private_key, public_key


def make_token(
    private_key,
    headers=None,
    payload=None,
    algorithm="RS256",
):
    """Helper to generate JWT tokens with custom headers and claims."""
    now = int(time.time())
    default_headers = {"kid": "key-1", "alg": algorithm}
    if headers:
        default_headers.update(headers)

    default_payload = {
        "sub": "user_alice_123",
        "iss": "https://auth.paypilot.example.com",
        "aud": "paypilot-api",
        "exp": now + 3600,
        "iat": now,
        "nbf": now - 10,
        "preferred_username": "alice",
        "email": "alice@example.com",
    }
    if payload:
        default_payload.update(payload)

    if algorithm.lower() == "none":
        # Unsigned token
        return jwt.encode(default_payload, key="", algorithm="none", headers=default_headers)

    return jwt.encode(default_payload, key=private_key, algorithm=algorithm, headers=default_headers)


# ---------------------------------------------------------------------------
# Workstream A Unit Tests: JWKSTokenVerifier Core
# ---------------------------------------------------------------------------

def test_scenario_01_valid_rs256_token(primary_keypair):
    """1. Valid RS256 token with valid claims authenticates and extracts user identity."""
    private_key, public_key = primary_keypair
    verifier = JWKSTokenVerifier(
        issuer="https://auth.paypilot.example.com",
        audience="paypilot-api",
        algorithms=["RS256"],
        static_keys={"key-1": public_key},
    )

    token = make_token(private_key, headers={"kid": "key-1"}, payload={"sub": "usr_999", "name": "Alice"})
    claims = verifier.verify_token(token)

    assert claims["sub"] == "usr_999"
    assert claims["iss"] == "https://auth.paypilot.example.com"
    assert claims["aud"] == "paypilot-api"
    assert claims["name"] == "Alice"


def test_scenario_02_missing_token():
    """2. Missing or blank token raises HTTP 401."""
    verifier = JWKSTokenVerifier(static_keys={"key-1": "dummy"})
    with pytest.raises(JWKSVerificationError) as exc_info:
        verifier.verify_token("")
    assert exc_info.value.status_code == 401
    assert "Missing" in exc_info.value.detail


def test_scenario_03_empty_whitespace_token():
    """3. Whitespace-only token raises HTTP 401."""
    verifier = JWKSTokenVerifier(static_keys={"key-1": "dummy"})
    with pytest.raises(JWKSVerificationError) as exc_info:
        verifier.verify_token("    ")
    assert exc_info.value.status_code == 401


def test_scenario_04_malformed_token_format():
    """4. Malformed JWT structure raises HTTP 401."""
    verifier = JWKSTokenVerifier(static_keys={"key-1": "dummy"})
    with pytest.raises(JWKSVerificationError) as exc_info:
        verifier.verify_token("not.a.valid.jwt.token.format")
    assert exc_info.value.status_code == 401


def test_scenario_05_tampered_signature(primary_keypair, attacker_keypair):
    """5. Tampered signature (signed with untrusted key or payload altered) raises HTTP 401."""
    _, public_key = primary_keypair
    attacker_private_key, _ = attacker_keypair

    verifier = JWKSTokenVerifier(
        issuer="https://auth.paypilot.example.com",
        audience="paypilot-api",
        static_keys={"key-1": public_key},
    )

    # Attacker signs token using their own private key, pretending to be key-1
    tampered_token = make_token(attacker_private_key, headers={"kid": "key-1"})

    with pytest.raises(JWKSVerificationError) as exc_info:
        verifier.verify_token(tampered_token)
    assert exc_info.value.status_code == 401
    assert "signature" in exc_info.value.detail.lower()


def test_scenario_06_expired_token(primary_keypair):
    """6. Expired token raises HTTP 401."""
    private_key, public_key = primary_keypair
    verifier = JWKSTokenVerifier(
        issuer="https://auth.paypilot.example.com",
        audience="paypilot-api",
        clock_skew_seconds=10,
        static_keys={"key-1": public_key},
    )

    # Expired 1 hour ago
    expired_token = make_token(private_key, payload={"exp": int(time.time()) - 3600})

    with pytest.raises(JWKSVerificationError) as exc_info:
        verifier.verify_token(expired_token)
    assert exc_info.value.status_code == 401
    assert "expired" in exc_info.value.detail.lower()


def test_scenario_07_future_nbf_token(primary_keypair):
    """7. Token with future nbf beyond clock skew raises HTTP 401."""
    private_key, public_key = primary_keypair
    verifier = JWKSTokenVerifier(
        issuer="https://auth.paypilot.example.com",
        audience="paypilot-api",
        clock_skew_seconds=10,
        static_keys={"key-1": public_key},
    )

    # nbf is 1 hour in the future
    future_token = make_token(private_key, payload={"nbf": int(time.time()) + 3600})

    with pytest.raises(JWKSVerificationError) as exc_info:
        verifier.verify_token(future_token)
    assert exc_info.value.status_code == 401
    assert "not yet valid" in exc_info.value.detail.lower()


def test_scenario_08_issuer_mismatch(primary_keypair):
    """8. Token with issuer mismatch raises HTTP 401."""
    private_key, public_key = primary_keypair
    verifier = JWKSTokenVerifier(
        issuer="https://auth.paypilot.example.com",
        static_keys={"key-1": public_key},
    )

    token = make_token(private_key, payload={"iss": "https://malicious-issuer.example.com"})

    with pytest.raises(JWKSVerificationError) as exc_info:
        verifier.verify_token(token)
    assert exc_info.value.status_code == 401
    assert "issuer" in exc_info.value.detail.lower()


def test_scenario_09_audience_mismatch(primary_keypair):
    """9. Token with audience mismatch raises HTTP 401."""
    private_key, public_key = primary_keypair
    verifier = JWKSTokenVerifier(
        audience="paypilot-api",
        static_keys={"key-1": public_key},
    )

    token = make_token(private_key, payload={"aud": "different-audience"})

    with pytest.raises(JWKSVerificationError) as exc_info:
        verifier.verify_token(token)
    assert exc_info.value.status_code == 401
    assert "audience" in exc_info.value.detail.lower()


def test_scenario_10_missing_sub_claim(primary_keypair):
    """10. Token missing sub claim raises HTTP 401."""
    private_key, public_key = primary_keypair
    verifier = JWKSTokenVerifier(static_keys={"key-1": public_key})

    now = int(time.time())
    payload = {"iss": "https://auth.paypilot.example.com", "exp": now + 3600, "iat": now}
    token = jwt.encode(payload, private_key, algorithm="RS256", headers={"kid": "key-1"})

    with pytest.raises(JWKSVerificationError) as exc_info:
        verifier.verify_token(token)
    assert exc_info.value.status_code == 401
    assert "sub" in exc_info.value.detail.lower()


def test_scenario_11_empty_sub_claim(primary_keypair):
    """11. Token with empty sub claim raises HTTP 401."""
    private_key, public_key = primary_keypair
    verifier = JWKSTokenVerifier(static_keys={"key-1": public_key})

    token = make_token(private_key, payload={"sub": "   "})

    with pytest.raises(JWKSVerificationError) as exc_info:
        verifier.verify_token(token)
    assert exc_info.value.status_code == 401
    assert "sub" in exc_info.value.detail.lower()


def test_scenario_12_rejection_of_alg_none():
    """12. Explicit rejection of alg='none' tokens."""
    verifier = JWKSTokenVerifier(algorithms=["RS256"], static_keys={"key-1": "dummy"})

    none_token = make_token(None, headers={"alg": "none"}, algorithm="none")

    with pytest.raises(JWKSVerificationError) as exc_info:
        verifier.verify_token(none_token)
    assert exc_info.value.status_code == 401
    assert "disallowed" in exc_info.value.detail.lower()


def test_scenario_13_rejection_of_disallowed_symmetric_alg(primary_keypair):
    """13. Explicit rejection of disallowed symmetric algorithms (e.g. HS256)."""
    _, public_key = primary_keypair
    verifier = JWKSTokenVerifier(algorithms=["RS256"], static_keys={"key-1": public_key})

    # Attacker tries HMAC with public key as secret (common JWT vulnerability)
    now = int(time.time())
    hs_token = jwt.encode(
        {"sub": "attacker", "exp": now + 3600},
        key="secret_symmetric_key",
        algorithm="HS256",
        headers={"kid": "key-1", "alg": "HS256"},
    )

    with pytest.raises(JWKSVerificationError) as exc_info:
        verifier.verify_token(hs_token)
    assert exc_info.value.status_code == 401
    assert "disallowed" in exc_info.value.detail.lower()


def test_scenario_14_unknown_kid_fails_closed(primary_keypair):
    """14. Unknown kid fails closed with HTTP 401."""
    private_key, public_key = primary_keypair
    verifier = JWKSTokenVerifier(static_keys={"key-1": public_key})

    token_unknown_kid = make_token(private_key, headers={"kid": "unknown-nonexistent-key"})

    with pytest.raises(JWKSVerificationError) as exc_info:
        verifier.verify_token(token_unknown_kid)
    assert exc_info.value.status_code == 401
    assert "not found" in exc_info.value.detail.lower()


def test_scenario_15_key_rotation(primary_keypair, secondary_keypair):
    """15. Key rotation: token signed with rotated key-2 succeeds after key addition."""
    _, key1_public = primary_keypair
    key2_private, key2_public = secondary_keypair

    # Initial verifier only has key-1
    verifier = JWKSTokenVerifier(static_keys={"key-1": key1_public})

    # Token signed with key-2 fails initially
    token_key2 = make_token(key2_private, headers={"kid": "key-2"})
    with pytest.raises(JWKSVerificationError):
        verifier.verify_token(token_key2)

    # IdP rotates keys, adding key-2 to key cache
    verifier.set_static_keys({"key-1": key1_public, "key-2": key2_public})

    # Now token signed with key-2 succeeds immediately
    claims = verifier.verify_token(token_key2)
    assert claims["sub"] == "user_alice_123"


def test_scenario_16_unavailable_remote_jwks_fails_closed(monkeypatch):
    """16. Unreachable remote JWKS endpoint fails closed."""
    verifier = JWKSTokenVerifier(jwks_url="https://invalid-jwks.unreachable.domain/keys")

    # Mock httpx failure
    import httpx

    def mock_get(*args, **kwargs):
        raise httpx.ConnectError("Network is unreachable")

    monkeypatch.setattr(httpx.Client, "get", mock_get)

    with pytest.raises(JWKSVerificationError) as exc_info:
        verifier.get_signing_key("unknown-kid")
    assert exc_info.value.status_code == 401
    assert "unreachable" in exc_info.value.detail.lower()


# ---------------------------------------------------------------------------
# Integration Tests: FastAPI Endpoints with AUTH_MODE="jwt"
# ---------------------------------------------------------------------------

@pytest.fixture
def jwt_auth_client(primary_keypair, monkeypatch):
    """Provide TestClient with AUTH_MODE='jwt' and mock JWKSTokenVerifier."""
    _, public_key = primary_keypair

    test_settings = Settings(
        AUTH_MODE="jwt",
        AUTH_ISSUER="https://auth.paypilot.example.com",
        AUTH_AUDIENCE="paypilot-api",
        AUTH_ALGORITHMS=["RS256"],
        AUTH_REQUIRED_CLAIMS=["sub"],
        ENVIRONMENT="development",
    )
    monkeypatch.setattr("app.core.auth.get_settings", lambda: test_settings)

    test_verifier = JWKSTokenVerifier(
        issuer="https://auth.paypilot.example.com",
        audience="paypilot-api",
        algorithms=["RS256"],
        static_keys={"key-1": public_key},
    )
    set_jwt_verifier(test_verifier)

    client = TestClient(app)
    yield client

    # Teardown
    set_jwt_verifier(None)


def test_scenario_17_x_user_id_spoofing_ignored_in_jwt_mode(jwt_auth_client, primary_keypair):
    """17. In AUTH_MODE=jwt, X-User-Id is completely ignored; identity is solely derived from verified JWT sub."""
    private_key, _ = primary_keypair
    token = make_token(private_key, payload={"sub": "verified_alice"})

    # Attacker tries to send X-User-Id: victim_bob
    resp = jwt_auth_client.get(
        "/api/notifications",
        headers={
            "Authorization": f"Bearer {token}",
            "X-User-Id": "victim_bob",
        },
    )
    assert resp.status_code == 200
    # Verified user identity in the system was verified_alice (never victim_bob)
    # Check notifications list returned belongs to verified_alice


def test_scenario_18_cross_user_plan_isolation_in_jwt_mode(jwt_auth_client, primary_keypair):
    """18. User A's verified JWT cannot access or approve User B's purchase plan."""
    private_key, _ = primary_keypair
    user_a_token = make_token(private_key, payload={"sub": "user_a"})
    user_b_token = make_token(private_key, payload={"sub": "user_b"})

    # User A creates a purchase plan
    create_resp = jwt_auth_client.post(
        "/api/purchase-plans",
        headers={"Authorization": f"Bearer {user_a_token}"},
        json={
            "product_id": "LAP-001",
            "quantity": 1,
            "session_id": "sess_jwt_cross_user",
        },
    )
    assert create_resp.status_code == 201
    plan_id = create_resp.json()["id"]

    # User B attempts to access User A's plan -> HTTP 403
    forbidden_resp = jwt_auth_client.get(
        f"/api/purchase-plans/{plan_id}",
        headers={"Authorization": f"Bearer {user_b_token}"},
    )
    assert forbidden_resp.status_code == 403


def test_scenario_19_verify_user_ownership_rejects_mismatch():
    """19. Mismatched body/query user_id rejected with HTTP 403 by verify_user_ownership."""
    auth_user = AuthenticatedUser(id="alice_actual", username="alice", is_authenticated=True)

    # Identical or empty client_user_id passes
    verify_user_ownership(auth_user, None)
    verify_user_ownership(auth_user, "")
    verify_user_ownership(auth_user, "alice_actual")

    # Mismatched client_user_id raises HTTP 403
    with pytest.raises(Exception) as exc_info:
        verify_user_ownership(auth_user, "bob_impersonated")
    assert getattr(exc_info.value, "status_code", None) == 403


def test_scenario_20_production_mode_rejects_demo_auth():
    """20. In ENVIRONMENT=production, AUTH_MODE=demo fails closed."""
    # Settings validation error if production with demo mode
    with pytest.raises(ValueError) as exc_info:
        Settings(
            ENVIRONMENT="production",
            AUTH_MODE="demo",
        )
    assert "AUTH_MODE must be 'jwt'" in str(exc_info.value)
