"""
Regression and security verification test suite for Public Preview and Production boundaries.

Covers:
1. Demo-mode privilege escalation prevention (X-User-Role / X-User-Id headers).
2. Fixed least-privilege role assignment in AUTH_MODE=demo.
3. User data isolation between guest_user and other users (e.g. ORD-099).
4. Strict production startup fail-closed rules (JWT requirement and PostgreSQL requirement).
5. Prevention of silent SQLite fallback in production environments.
"""

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.main import app
from app.core.config import Settings, get_settings
from app.core.auth import AuthenticatedUser, get_current_user
from app.db.session import resolve_database_url

client = TestClient(app)


# ==============================================================================
# 1. Demo Mode Privilege Escalation Defense
# ==============================================================================

def test_demo_mode_blocks_admin_privilege_escalation_via_x_user_role():
    """Client cannot escalate to admin by supplying X-User-Role: admin header in demo mode."""
    response = client.get(
        "/api/payments/reconciliation/report",
        headers={"X-User-Role": "admin"},
    )
    assert response.status_code == 403
    assert "Administrative privileges required" in response.json()["detail"]


def test_demo_mode_blocks_admin_privilege_escalation_via_x_user_id():
    """Client cannot escalate to admin by supplying X-User-Id: admin or admin_user in demo mode."""
    for admin_id in ["admin", "admin_user", "administrator", "root"]:
        response = client.get(
            "/api/payments/reconciliation/report",
            headers={"X-User-Id": admin_id},
        )
        assert response.status_code == 403
        assert "Administrative privileges required" in response.json()["detail"]


def test_demo_mode_blocks_combined_spoofed_headers():
    """Client combining both spoofed X-User-Id and X-User-Role headers is still rejected with 403."""
    response = client.get(
        "/api/payments/reconciliation/report",
        headers={
            "X-User-Id": "admin",
            "X-User-Role": "admin",
            "Authorization": "Bearer admin",
        },
    )
    assert response.status_code == 403
    assert "Administrative privileges required" in response.json()["detail"]


def test_demo_mode_least_privilege_role_invariance():
    """In demo mode, every request receives fixed role='user' regardless of client headers."""
    response = client.get(
        "/api/orders",
        headers={
            "X-User-Role": "admin",
            "X-User-Id": "custom_attacker_99",
            "Authorization": "Bearer superuser_token",
        },
    )
    assert response.status_code == 200
    # The authenticated identity is strictly guest_user, not custom_attacker_99
    orders = response.json()
    assert isinstance(orders, list)
    for order in orders:
        assert order["user_id"] == "guest_user"


# ==============================================================================
# 2. Shared Demo Account Data Isolation
# ==============================================================================

def test_shared_guest_cannot_access_other_users_private_orders():
    """Shared guest_user cannot access orders belonging to another user (e.g. ORD-099 for other_user_88)."""
    # Demo visitor attempts to access ORD-099
    response = client.get("/api/orders/ORD-099")
    assert response.status_code == 403
    assert "Access denied" in response.json()["detail"]


def test_client_cannot_spoof_x_user_id_to_steal_other_user_orders():
    """Client passing X-User-Id: other_user_88 cannot view ORD-099."""
    response = client.get(
        "/api/orders/ORD-099",
        headers={"X-User-Id": "other_user_88"},
    )
    assert response.status_code == 403
    assert "Access denied" in response.json()["detail"]


# ==============================================================================
# 3. Production Configuration & Fail-Closed Guardrails
# ==============================================================================

def test_production_mode_requires_jwt_auth():
    """Settings validation fails if ENVIRONMENT=production and AUTH_MODE=demo."""
    with pytest.raises(ValidationError) as exc_info:
        Settings(
            ENVIRONMENT="production",
            AUTH_MODE="demo",
            AUTH_ISSUER="https://auth.example.com",
            AUTH_JWKS_URL="https://auth.example.com/jwks",
            DATABASE_URL="postgresql+psycopg://user:pass@localhost:5432/db",
        )
    assert "AUTH_MODE must be 'jwt' in production environment" in str(exc_info.value)


def test_production_mode_requires_database_url():
    """Settings validation fails if ENVIRONMENT=production and DATABASE_URL is missing."""
    with pytest.raises(ValidationError) as exc_info:
        Settings(
            ENVIRONMENT="production",
            AUTH_MODE="jwt",
            AUTH_ISSUER="https://auth.example.com",
            AUTH_JWKS_URL="https://auth.example.com/jwks",
            DATABASE_URL=None,
        )
    assert "DATABASE_URL must be configured when ENVIRONMENT='production'" in str(exc_info.value)


def test_production_mode_forbids_sqlite_in_production():
    """Settings validation fails if ENVIRONMENT=production and DATABASE_URL is SQLite."""
    with pytest.raises(ValidationError) as exc_info:
        Settings(
            ENVIRONMENT="production",
            AUTH_MODE="jwt",
            AUTH_ISSUER="https://auth.example.com",
            AUTH_JWKS_URL="https://auth.example.com/jwks",
            DATABASE_URL="sqlite:///./paypilot.db",
        )
    assert "SQLite is forbidden in production environment" in str(exc_info.value)


def test_resolve_database_url_blocks_silent_fallback_in_production(monkeypatch):
    """resolve_database_url raises RuntimeError if DATABASE_URL is missing in production."""
    settings = get_settings()
    monkeypatch.setattr(settings, "ENVIRONMENT", "production")
    monkeypatch.setattr(settings, "DATABASE_URL", None)

    with pytest.raises(RuntimeError) as exc_info:
        resolve_database_url(None)
    assert "Refusing silent fallback to SQLite" in str(exc_info.value)
