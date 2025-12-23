"""
Shared test fixtures and configuration for pytest.

This module provides common fixtures used across all test modules.
"""

import os
import pytest
import sys
from pathlib import Path
from fastapi.testclient import TestClient

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Configure test environment variables before importing app
os.environ["API_KEY_ENABLED"] = "false"
os.environ["RATE_LIMIT_ENABLED"] = "false"
os.environ["ENVIRONMENT"] = "development"
os.environ["CORS_ORIGINS"] = "http://localhost:3000,http://testserver"

from api.main import app


@pytest.fixture
def client():
    """
    Create a test client for the FastAPI app.

    This fixture provides a TestClient instance that can be used
    to make requests to the API endpoints in tests.
    """
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def authenticated_client():
    """
    Create an authenticated test client for testing API key auth.

    Sets up environment with API key authentication enabled and
    provides the valid API key in request headers.
    """
    # Enable API key auth for this test
    os.environ["API_KEY_ENABLED"] = "true"
    os.environ["API_KEYS"] = "test_key_123,test_key_456"

    # Reload settings
    from api.config import Settings
    test_settings = Settings()

    with TestClient(app) as test_client:
        # Add API key to all requests
        test_client.headers = {"X-API-Key": "test_key_123"}
        yield test_client

    # Reset to disabled after test
    os.environ["API_KEY_ENABLED"] = "false"
