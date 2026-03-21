"""
API Dependencies

FastAPI dependency injection functions.
"""

from collections.abc import AsyncGenerator

from workflow_orchestration_queue.state.store.github_queue import GitHubQueue


async def get_queue() -> AsyncGenerator[GitHubQueue, None]:
    """Dependency injection for the GitHub queue implementation."""
    from workflow_orchestration_queue.config.settings import settings

    queue = GitHubQueue(
        token=settings.github_token,
        org=settings.github_org,
        repo=settings.github_repo,
    )
    try:
        yield queue
    finally:
        await queue.close()
