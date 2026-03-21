"""
Pytest Configuration

Shared fixtures and configuration for tests.
"""

import pytest


@pytest.fixture
def anyio_backend() -> str:
    """Configure anyio to use asyncio backend."""
    return "asyncio"
