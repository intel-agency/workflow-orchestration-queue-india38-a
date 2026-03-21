"""
Webhook Routes

Handles incoming webhooks from GitHub and other providers.
"""

import hashlib
import hmac
from typing import Any

from fastapi import APIRouter, Header, HTTPException, Request

from workflow_orchestration_queue.config.settings import settings
from workflow_orchestration_queue.ear.handlers import github as github_handler

router = APIRouter()


def verify_github_signature(request: Request, x_hub_signature_256: str = Header(None)) -> None:
    """Verify GitHub webhook signature using HMAC SHA256."""
    if not x_hub_signature_256:
        raise HTTPException(status_code=401, detail="X-Hub-Signature-256 missing")

    if not settings.webhook_secret:
        raise HTTPException(status_code=500, detail="Webhook secret not configured")

    # Note: Body must be read in the handler, this is a placeholder
    # In production, we'd use a middleware or dependency that caches the body


@router.post("/github")
async def handle_github_webhook(
    request: Request,
    x_github_event: str = Header(None, alias="X-GitHub-Event"),
    x_hub_signature_256: str = Header(None, alias="X-Hub-Signature-256"),
) -> dict[str, str]:
    """Handle incoming GitHub webhook events."""
    if not x_github_event:
        raise HTTPException(status_code=400, detail="X-GitHub-Event header missing")

    # Read and verify signature
    body = await request.body()
    if settings.webhook_secret and x_hub_signature_256:
        expected_sig = (
            "sha256="
            + hmac.new(
                settings.webhook_secret.encode(),
                body,
                hashlib.sha256,
            ).hexdigest()
        )
        if not hmac.compare_digest(expected_sig, x_hub_signature_256):
            raise HTTPException(status_code=401, detail="Invalid signature")

    # Parse payload
    try:
        payload: dict[str, Any] = await request.json()
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Invalid JSON payload") from exc

    # Route to appropriate handler
    return await github_handler.handle_event(x_github_event, payload)
