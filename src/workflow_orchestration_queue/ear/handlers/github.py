"""
GitHub Webhook Handler

Processes incoming GitHub webhook events and routes them to appropriate processors.
"""

from typing import Any

from workflow_orchestration_queue.state.models.work_item import TaskType, WorkItem, WorkItemStatus


async def handle_event(event_type: str, payload: dict[str, Any]) -> dict[str, str]:
    """Route GitHub webhook events to appropriate handlers.

    Args:
        event_type: The X-GitHub-Event header value
        payload: The parsed JSON payload

    Returns:
        Response dict with status information
    """
    if event_type == "issues":
        return await _handle_issues_event(payload)

    if event_type == "push":
        return await _handle_push_event(payload)

    if event_type == "pull_request":
        return await _handle_pull_request_event(payload)

    return {"status": "ignored", "reason": f"No handler for event type: {event_type}"}


async def _handle_issues_event(payload: dict[str, Any]) -> dict[str, str]:
    """Handle GitHub issues webhook events."""
    action = payload.get("action")

    if action == "opened":
        issue = payload.get("issue", {})
        labels = [label["name"] for label in issue.get("labels", [])]
        title = issue.get("title", "")

        # Check if this is an actionable task
        is_plan = "[Application Plan]" in title or "agent:plan" in labels
        is_task = "agent:task" in labels

        if is_plan or is_task:
            task_type = TaskType.PLAN if is_plan else TaskType.IMPLEMENT

            work_item = WorkItem(
                id=str(issue.get("id", "")),
                issue_number=issue.get("number", 0),
                source_url=issue.get("html_url", ""),
                target_repo_slug=payload.get("repository", {}).get("full_name", ""),
                task_type=task_type,
                context_body=issue.get("body") or "",
                status=WorkItemStatus.QUEUED,
                node_id=issue.get("node_id", ""),
            )

            # Queue the work item
            # Note: In production, this would use dependency injection
            return {"status": "accepted", "item_id": work_item.id}

    return {"status": "ignored", "reason": f"No actionable mapping for action: {action}"}


async def _handle_push_event(payload: dict[str, Any]) -> dict[str, str]:
    """Handle GitHub push webhook events."""
    # Placeholder for push event handling
    return {"status": "ignored", "reason": "Push events not yet implemented"}


async def _handle_pull_request_event(payload: dict[str, Any]) -> dict[str, str]:
    """Handle GitHub pull request webhook events."""
    # Placeholder for PR event handling
    return {"status": "ignored", "reason": "Pull request events not yet implemented"}
