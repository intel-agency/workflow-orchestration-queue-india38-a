"""
Tests for the main FastAPI application.
"""

import pytest
from fastapi.testclient import TestClient

from workflow_orchestration_queue.main import app

HTTP_OK = 200


@pytest.fixture
def client() -> TestClient:
    """Create a test client for the FastAPI app."""
    return TestClient(app)


def test_health_check(client: TestClient) -> None:
    """Test the health check endpoint returns online status."""
    response = client.get("/health")
    assert response.status_code == HTTP_OK
    data = response.json()
    assert data["status"] == "online"
    assert data["system"] == "OS-APOW Notifier"


def test_readiness_check(client: TestClient) -> None:
    """Test the readiness endpoint returns ready status."""
    response = client.get("/ready")
    assert response.status_code == HTTP_OK
    data = response.json()
    assert data["status"] == "ready"
    assert data["system"] == "OS-APOW Notifier"
