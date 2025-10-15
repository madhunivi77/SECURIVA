import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


class ToolCallLogger:
    """
    Logger for MCP tool calls with both JSON and human-readable output.
    Logs are stored in backend/logs/ directory.
    """

    def __init__(self, enabled: bool = True, log_dir: str = None):
        self.enabled = enabled

        # Set up log directory
        if log_dir is None:
            # Default to backend/logs/
            backend_dir = Path(__file__).parent.parent.parent
            log_dir = backend_dir / "logs"
        else:
            log_dir = Path(log_dir)

        log_dir.mkdir(parents=True, exist_ok=True)

        self.json_log_path = log_dir / "tool_calls.json"
        self.text_log_path = log_dir / "tool_calls.log"

        # Set up text logger
        self.logger = logging.getLogger("ToolCallLogger")
        self.logger.setLevel(logging.INFO)

        # Remove existing handlers to avoid duplicates
        self.logger.handlers.clear()

        # File handler for human-readable logs
        file_handler = logging.FileHandler(self.text_log_path)
        file_handler.setLevel(logging.INFO)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)

        # Console handler for real-time visibility
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '🔧 [TOOL] %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

    def log_tool_call(
        self,
        session_id: str,
        tool_name: str,
        arguments: Dict[str, Any],
        result: Optional[Any] = None,
        error: Optional[str] = None,
        duration_ms: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Log a tool call with all relevant information.

        Args:
            session_id: Unique identifier for the chat session
            tool_name: Name of the tool being called
            arguments: Tool arguments/parameters
            result: Tool execution result (if successful)
            error: Error message (if failed)
            duration_ms: Execution duration in milliseconds
            metadata: Additional metadata (user_id, model, etc.)
        """
        if not self.enabled:
            return

        timestamp = datetime.utcnow().isoformat()
        status = "error" if error else "success"

        # Create log entry
        log_entry = {
            "timestamp": timestamp,
            "session_id": session_id,
            "tool_name": tool_name,
            "arguments": arguments,
            "status": status,
            "duration_ms": duration_ms,
        }

        if result is not None:
            # Truncate large results for JSON log
            result_str = str(result)
            if len(result_str) > 1000:
                log_entry["result"] = result_str[:1000] + "... (truncated)"
                log_entry["result_length"] = len(result_str)
            else:
                log_entry["result"] = result_str

        if error:
            log_entry["error"] = error

        if metadata:
            log_entry["metadata"] = metadata

        # Write to JSON log (one JSON object per line for easy parsing)
        try:
            with open(self.json_log_path, "a") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception as e:
            self.logger.error(f"Failed to write JSON log: {e}")

        # Write human-readable log
        duration_str = f"{duration_ms:.2f}ms" if duration_ms else "N/A"
        args_str = json.dumps(arguments, indent=2) if arguments else "{}"

        if error:
            self.logger.error(
                f"Tool '{tool_name}' FAILED | Session: {session_id} | Duration: {duration_str}\n"
                f"  Arguments: {args_str}\n"
                f"  Error: {error}"
            )
        else:
            result_preview = str(result)[:200] if result else "No result"
            self.logger.info(
                f"Tool '{tool_name}' SUCCESS | Session: {session_id} | Duration: {duration_str}\n"
                f"  Arguments: {args_str}\n"
                f"  Result: {result_preview}{'...' if result and len(str(result)) > 200 else ''}"
            )

    def get_recent_logs(self, limit: int = 100) -> list:
        """
        Retrieve recent tool call logs from JSON file.

        Args:
            limit: Maximum number of logs to return

        Returns:
            List of log entries (most recent first)
        """
        if not self.json_log_path.exists():
            return []

        try:
            logs = []
            with open(self.json_log_path, "r") as f:
                for line in f:
                    if line.strip():
                        logs.append(json.loads(line))

            # Return most recent first
            return logs[-limit:][::-1]
        except Exception as e:
            self.logger.error(f"Failed to read logs: {e}")
            return []

    def get_session_logs(self, session_id: str) -> list:
        """
        Retrieve all logs for a specific session.

        Args:
            session_id: Session identifier

        Returns:
            List of log entries for the session
        """
        if not self.json_log_path.exists():
            return []

        try:
            logs = []
            with open(self.json_log_path, "r") as f:
                for line in f:
                    if line.strip():
                        log_entry = json.loads(line)
                        if log_entry.get("session_id") == session_id:
                            logs.append(log_entry)
            return logs
        except Exception as e:
            self.logger.error(f"Failed to read session logs: {e}")
            return []


# Create global logger instance
_logger_instance = None


def get_tool_logger() -> ToolCallLogger:
    """Get or create the global ToolCallLogger instance."""
    global _logger_instance
    if _logger_instance is None:
        enabled = os.getenv("ENABLE_TOOL_LOGGING", "true").lower() == "true"
        _logger_instance = ToolCallLogger(enabled=enabled)
    return _logger_instance
