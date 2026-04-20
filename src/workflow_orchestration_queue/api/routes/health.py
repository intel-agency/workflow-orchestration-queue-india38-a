"""
Health Check Endpoint

Provides health status for the OS-APOW service.
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint for monitoring and load balancers."""
    return {"status": "online", "system": "OS-APOW Notifier"}


@router.get("/ready")
async def readiness_check() -> dict[str, str]:
    """Readiness check endpoint - verifies the service is ready to accept traffic."""
    return {"status": "ready", "system": "OS-APOW Notifier"}
