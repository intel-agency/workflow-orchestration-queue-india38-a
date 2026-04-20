"""
OS-APOW Notifier

Handles sending notifications and updates to external systems.
"""

import logging
from typing import Any

from workflow_orchestration_queue.state.models.work_item import WorkItem, scrub_secrets

logger = logging.getLogger("OS-APOW")


class Notifier:
    """Handles notification delivery for the system."""

    def __init__(self, queue: Any) -> None:
        """Initialize the notifier.

        Args:
            queue: The queue to use for posting updates
        """
        self.queue = queue

    async def notify_start(self, item: WorkItem, _sentinel_id: str) -> None:
        """Notify that work has started on an item.

        Args:
            item: The work item being processed
            sentinel_id: The ID of the sentinel processing the item
        """
        logger.info(f"Notifying start for task #{item.issue_number}")

    async def notify_progress(
        self,
        item: WorkItem,
        _sentinel_id: str,
        message: str,
    ) -> None:
        """Notify about progress on an item.

        Args:
            item: The work item being processed
            sentinel_id: The ID of the sentinel processing the item
            message: Progress message
        """
        safe_message = scrub_secrets(message)
        logger.info(f"Progress on task #{item.issue_number}: {safe_message}")

    async def notify_complete(
        self,
        item: WorkItem,
        _sentinel_id: str,
        success: bool,
        message: str | None = None,
    ) -> None:
        """Notify that work has completed on an item.

        Args:
            item: The work item that was processed
            sentinel_id: The ID of the sentinel processing the item
            success: Whether the task completed successfully
            message: Optional completion message
        """
        status = "completed successfully" if success else "failed"
        logger.info(f"Task #{item.issue_number} {status}")
        if message:
            safe_message = scrub_secrets(message)
            logger.info(f"Details: {safe_message}")
