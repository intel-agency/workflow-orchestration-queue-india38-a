"""
Tests for the main FastAPI application.
"""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client() -> TestClient:
    """Create a test client for the FastAPI app."""
    from workflow_orchestration_queue.main import app

    return TestClient(app)


def test_health_check(client: TestClient) -> None:
    """Test the health check endpoint returns online status."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert data["system"] == "OS-APOW Notifier"


def test_readiness_check(client: TestClient) -> None:
    """Test the readiness endpoint returns ready status."""
    response = client.get("/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert data["system"] == "OS-APOW Notifier"
