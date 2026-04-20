"""
OS-APOW Orchestrator

High-level orchestration logic for coordinating task execution.
"""

from workflow_orchestration_queue.state.models.work_item import TaskType, WorkItem


class Orchestrator:
    """Coordinates task execution across the system."""

    def __init__(self) -> None:
        """Initialize the orchestrator."""
        self._workflow_map: dict[TaskType, str] = {
            TaskType.PLAN: "create-app-plan.md",
            TaskType.IMPLEMENT: "perform-task.md",
            TaskType.BUGFIX: "recover-from-error.md",
        }

    def get_workflow(self, task_type: TaskType) -> str:
        """Get the workflow file for a task type.

        Args:
            task_type: The type of task to get workflow for

        Returns:
            The workflow filename
        """
        return self._workflow_map.get(task_type, "perform-task.md")

    def build_instruction(self, item: WorkItem) -> str:
        """Build the instruction for a work item.

        Args:
            item: The work item to build instruction for

        Returns:
            The instruction string
        """
        workflow = self.get_workflow(item.task_type)
        return f"Execute workflow {workflow} for context: {item.source_url}"
