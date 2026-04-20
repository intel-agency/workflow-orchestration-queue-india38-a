"""
OS-APOW Executor

Handles execution of workflows and shell commands.
"""

import asyncio
import logging
import subprocess

logger = logging.getLogger("OS-APOW")


class Executor:
    """Handles execution of commands and workflows."""

    def __init__(self, shell_bridge_path: str = "./scripts/devcontainer-opencode.sh") -> None:
        """Initialize the executor.

        Args:
            shell_bridge_path: Path to the shell bridge script
        """
        self.shell_bridge_path = shell_bridge_path

    async def run_command(
        self,
        args: list[str],
        timeout: int | None = None,
    ) -> subprocess.CompletedProcess[str]:
        """Run a shell command asynchronously.

        Args:
            args: Command and arguments to run
            timeout: Maximum seconds to wait

        Returns:
            CompletedProcess with results
        """
        try:
            logger.info(f"Executing: {' '.join(args)}")
            process = await asyncio.create_subprocess_exec(
                *args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout,
                )
            except TimeoutError:
                logger.warning(f"Command timed out after {timeout}s — killing")
                process.kill()
                stdout, stderr = await process.communicate()
                return subprocess.CompletedProcess(
                    args=args,
                    returncode=-1,
                    stdout=stdout.decode().strip() if stdout else "",
                    stderr=f"TIMEOUT after {timeout}s\n"
                    + (stderr.decode().strip() if stderr else ""),
                )

            return subprocess.CompletedProcess(
                args=args,
                returncode=process.returncode if process.returncode is not None else -1,
                stdout=stdout.decode().strip() if stdout else "",
                stderr=stderr.decode().strip() if stderr else "",
            )
        except Exception:
            logger.exception("Command execution error")
            raise

    async def initialize_environment(self) -> bool:
        """Initialize the execution environment.

        Returns:
            True if initialization succeeded
        """
        result = await self.run_command([self.shell_bridge_path, "up"], timeout=300)
        return result.returncode == 0

    async def start_server(self) -> bool:
        """Start the opencode server.

        Returns:
            True if server started successfully
        """
        result = await self.run_command([self.shell_bridge_path, "start"], timeout=120)
        return result.returncode == 0

    async def execute_workflow(self, instruction: str, timeout: int = 5700) -> bool:
        """Execute a workflow instruction.

        Args:
            instruction: The instruction to execute
            timeout: Maximum seconds to wait

        Returns:
            True if execution succeeded
        """
        result = await self.run_command(
            [self.shell_bridge_path, "prompt", instruction],
            timeout=timeout,
        )
        return result.returncode == 0

    async def stop_environment(self) -> bool:
        """Stop the execution environment.

        Returns:
            True if stop succeeded
        """
        result = await self.run_command([self.shell_bridge_path, "stop"], timeout=60)
        return result.returncode == 0
