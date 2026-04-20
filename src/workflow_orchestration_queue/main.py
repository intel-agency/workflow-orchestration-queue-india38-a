"""
OS-APOW FastAPI Application Entry Point

This module provides the main FastAPI application and serves as the
entry point for the EAR (Event Notifier) component.
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from workflow_orchestration_queue.api.routes import health, webhooks
from workflow_orchestration_queue.config.settings import settings


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan manager for startup/shutdown events."""
    # Startup
    settings.validate_required()
    yield
    # Shutdown


app = FastAPI(
    title="OS-APOW Workflow Orchestration Queue",
    description="Headless agentic orchestration platform for GitHub Issues",
    version="0.1.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, tags=["health"])
app.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])


def run_dev() -> None:
    """Run the development server."""
    uvicorn.run(
        "workflow_orchestration_queue.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )


if __name__ == "__main__":
    run_dev()
