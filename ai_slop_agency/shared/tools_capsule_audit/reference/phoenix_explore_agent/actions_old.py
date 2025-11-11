"""Action execution for explore agent."""

from typing import Any, Dict

from ...agent_api import ConstitutionalViolationError
from ...phoenix_logging import get_logger


_logger = get_logger("phoenix.explore_agent.actions")


class ActionExecutor:
    """Executes individual steps in the exploration process."""

    def __init__(self, api: Any):
        if api is None:
            raise ValueError("Agent API instance is required")
        self._api = api

    def execute_step(self, step: str) -> Dict[str, Any]:
        """Execute a single step via AgentAPI tools."""
        try:
            # Normalize step: remove backticks, trailing pipes/descriptions
            step = step.strip()
            if step.startswith("`") and step.endswith("`"):
                step = step[1:-1].strip()
            # Remove pipe-delimited description
            if "|" in step:
                step = step.split("|")[0].strip()
            # Remove trailing punctuation
            step = step.rstrip(".,;:")

            action, _, remainder = step.partition(":")
            action = action.lower().strip()
            remainder = remainder.strip()

            if action == "filesystem":
                return self._execute_filesystem_step(remainder)
            if action in {"system", "shell"}:
                return self._execute_system_step(remainder)

            # Fallback heuristics for natural language steps
            if "list" in step.lower():
                return self._execute_filesystem_step(f"list {remainder or '.'}")
            if "read" in step.lower():
                return self._execute_filesystem_step(f"read {remainder}")
            if "shell" in step.lower() or "run" in step.lower():
                command = remainder or step
                return self._execute_system_step(command)

            return {
                "success": False,
                "detail": f"Unsupported step format: {step}",
            }

        except ConstitutionalViolationError as exc:
            _logger.warning(
                "Constitutional violation during execution",
                step=step,
                error=str(exc),
            )
            return {
                "success": False,
                "detail": f"Constitutional violation: {exc.message}",
                "violation": exc.to_dict(),
            }
        except Exception as exc:  # Broad to keep agent resilient in MVP
            _logger.warning(
                "Execution step failed",
                step=step,
                error=str(exc),
            )
            return {
                "success": False,
                "detail": f"Execution error: {exc}",
            }

    def _execute_filesystem_step(self, instruction: str) -> Dict[str, Any]:
        fs_api = getattr(self._api, "filesystem", None)
        if fs_api is None:
            return {"success": False, "detail": "Filesystem API is unavailable"}

        verb, _, target = instruction.partition(" ")
        verb = verb.lower().strip()
        target = target.strip() or "."

        try:
            if verb == "list":
                listing = fs_api.list_directory(target)
                return {
                    "success": True,
                    "detail": f"Listed {target}: {listing}",
                    "data": listing,
                    "type": "filesystem.list_directory",
                }
            if verb == "read":
                # Check if target is a directory and suggest list instead
                import os

                if os.path.isdir(target):
                    _logger.info(
                        "Cannot read directory, using list instead",
                        target=target,
                    )
                    listing = fs_api.list_directory(target)
                    return {
                        "success": True,
                        "detail": f"Cannot read directory {target}, listed instead: {listing}",
                        "data": listing,
                        "type": "filesystem.list_directory",
                    }
                content = fs_api.read(target)
                return {
                    "success": True,
                    "detail": f"Read {target}: {content}",
                    "data": content,
                    "type": "filesystem.read",
                }
            if verb == "write":
                path, _, content = target.partition(" ")
                fs_api.write(path, content)
                return {
                    "success": True,
                    "detail": f"Wrote to {path}",
                    "type": "filesystem.write",
                }
        except FileNotFoundError as exc:
            _logger.info(
                "Filesystem target not found",
                verb=verb,
                target=target,
                error=str(exc),
            )
            return {
                "success": False,
                "detail": f"Filesystem target not found: {target}",
                "error": "file_not_found",
            }
        except OSError as exc:
            _logger.warning(
                "Filesystem operation failed",
                verb=verb,
                target=target,
                error=str(exc),
            )
            return {
                "success": False,
                "detail": f"Filesystem error for {target}: {exc}",
                "error": "filesystem_error",
            }

        return {"success": False, "detail": f"Unknown filesystem verb: {verb}"}

    def _execute_system_step(self, instruction: str) -> Dict[str, Any]:
        system_api = getattr(self._api, "system", None)
        if system_api is None:
            return {"success": False, "detail": "System API is unavailable"}

        command = instruction.strip()
        if not command:
            return {"success": False, "detail": "Shell command is empty"}

        try:
            result = system_api.run_shell_command(command)
        except TimeoutError as exc:
            _logger.warning(
                "Shell command timed out",
                command=command,
                error=str(exc),
            )
            return {
                "success": False,
                "detail": f"Command timeout: {command}",
                "error": "timeout",
            }
        except Exception as exc:
            _logger.warning(
                "Shell command failed",
                command=command,
                error=str(exc),
            )
            return {
                "success": False,
                "detail": f"Command error: {exc}",
                "error": "command_error",
            }

        success = result.get("exit_code", 1) == 0
        return {
            "success": success,
            "detail": f"Command `{command}` exited with {result.get('exit_code')}",
            "data": result,
            "type": "system.run_shell_command",
        }


__all__ = ["ActionExecutor"]
