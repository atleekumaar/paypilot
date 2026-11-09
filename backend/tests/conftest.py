"""Global test configuration and fixtures."""

import os
import pytest

# Ensure automated test suite runs in safe isolated test mode
os.environ["PAYPAL_MOCK_ENABLED"] = "true"
os.environ["ENVIRONMENT"] = "development"
os.environ["AUTH_MODE"] = "demo"

from app.core.config import get_settings
get_settings.cache_clear()


@pytest.fixture(autouse=True, scope="session")
def setup_test_suite():
    """Session-level setup guaranteeing mock isolation for automated tests."""
    os.environ["PAYPAL_MOCK_ENABLED"] = "true"
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()

