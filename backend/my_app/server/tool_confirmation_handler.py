"""
Tool Confirmation Handler

Manages the workflow for getting user confirmation before executing tools.
Stores pending confirmations and processes user responses.
"""

import json
import uuid
from typing import Dict, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from .tool_confirmation_config import (
    requires_confirmation,
    get_confirmation_rule,
    format_confirmation_message
)


@dataclass
class PendingConfirmation:
    """Represents a tool execution pending user confirmation."""
    confirmation_id: str
    tool_name: str
    tool_args: dict
    user_id: Optional[str]
    session_id: Optional[str]
    created_at: datetime
    expires_at: datetime
    confirmation_message: str
    status: str = "pending"  # "pending", "approved", "denied", "expired"
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['expires_at'] = self.expires_at.isoformat()
        return data
    
    def is_expired(self) -> bool:
        """Check if this confirmation has expired."""
        return datetime.now() > self.expires_at


class ToolConfirmationHandler:
    """
    Manages tool confirmation workflow.
    
    In a production environment, this should use a persistent store (Redis, DynamoDB, etc.)
    instead of in-memory storage.
    """
    
    def __init__(self, confirmation_timeout_seconds: int = 300):
        """
        Initialize the confirmation handler.
        
        Args:
            confirmation_timeout_seconds: How long confirmations are valid (default 5 minutes)
        """
        self.confirmation_timeout = confirmation_timeout_seconds
        self.pending_confirmations: Dict[str, PendingConfirmation] = {}
        self.session_confirmations: Dict[str, list[str]] = {}  # session_id -> [confirmation_ids]
    
    def create_confirmation_request(
        self,
        tool_name: str,
        tool_args: dict,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> tuple[str, str]:
        """
        Create a new confirmation request.
        
        Args:
            tool_name: Name of the tool to execute
            tool_args: Arguments to pass to the tool
            user_id: Optional user ID
            session_id: Optional session ID for tracking
        
        Returns:
            Tuple of (confirmation_id, confirmation_message)
        """
        confirmation_id = str(uuid.uuid4())
        
        # Generate the confirmation message
        confirmation_message = format_confirmation_message(tool_name, tool_args)
        
        # Add instructions for user response
        confirmation_message += "\n\n**Reply with:**\n"
        confirmation_message += f"- `yes` or `approve` to proceed\n"
        confirmation_message += f"- `no` or `cancel` to cancel\n"
        confirmation_message += f"- `modify` to change parameters\n"
        
        # Create pending confirmation
        pending = PendingConfirmation(
            confirmation_id=confirmation_id,
            tool_name=tool_name,
            tool_args=tool_args,
            user_id=user_id,
            session_id=session_id,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(seconds=self.confirmation_timeout),
            confirmation_message=confirmation_message,
            status="pending"
        )
        
        # Store it
        self.pending_confirmations[confirmation_id] = pending
        
        # Track by session
        if session_id:
            if session_id not in self.session_confirmations:
                self.session_confirmations[session_id] = []
            self.session_confirmations[session_id].append(confirmation_id)
        
        return confirmation_id, confirmation_message
    
    def get_pending_confirmation(
        self,
        session_id: Optional[str] = None,
        confirmation_id: Optional[str] = None
    ) -> Optional[PendingConfirmation]:
        """
        Get a pending confirmation by session or confirmation ID.
        
        Args:
            session_id: Session to get latest pending confirmation from
            confirmation_id: Specific confirmation ID to retrieve
        
        Returns:
            PendingConfirmation if found and valid, None otherwise
        """
        if confirmation_id:
            pending = self.pending_confirmations.get(confirmation_id)
            if pending and not pending.is_expired() and pending.status == "pending":
                return pending
            return None
        
        if session_id and session_id in self.session_confirmations:
            # Get the latest pending confirmation for this session
            for conf_id in reversed(self.session_confirmations[session_id]):
                pending = self.pending_confirmations.get(conf_id)
                if pending and not pending.is_expired() and pending.status == "pending":
                    return pending
        
        return None
    
    def approve_confirmation(
        self,
        session_id: Optional[str] = None,
        confirmation_id: Optional[str] = None
    ) -> Optional[tuple[str, dict]]:
        """
        Approve a pending confirmation.
        
        Returns:
            Tuple of (tool_name, tool_args) if approved, None otherwise
        """
        pending = self.get_pending_confirmation(session_id, confirmation_id)
        if not pending:
            return None
        
        pending.status = "approved"
        return (pending.tool_name, pending.tool_args)
    
    def deny_confirmation(
        self,
        session_id: Optional[str] = None,
        confirmation_id: Optional[str] = None
    ) -> bool:
        """
        Deny a pending confirmation.
        
        Returns:
            True if denied successfully, False if not found
        """
        pending = self.get_pending_confirmation(session_id, confirmation_id)
        if not pending:
            return False
        
        pending.status = "denied"
        return True
    
    def process_user_response(
        self,
        user_message: str,
        session_id: Optional[str] = None
    ) -> tuple[str, Optional[tuple[str, dict]]]:
        """
        Process a user's response to a confirmation request.
        
        Args:
            user_message: The user's message
            session_id: Session ID for context
        
        Returns:
            Tuple of (response_type, tool_info)
            - response_type: "approved", "denied", "no_pending", "expired", or "unclear"
            - tool_info: (tool_name, tool_args) if approved, None otherwise
        """
        # Check if there's a pending confirmation
        pending = self.get_pending_confirmation(session_id=session_id)
        
        if not pending:
            return ("no_pending", None)
        
        if pending.is_expired():
            pending.status = "expired"
            return ("expired", None)
        
        # Parse user response
        message_lower = user_message.lower().strip()
        
        # Approval keywords
        if any(keyword in message_lower for keyword in ["yes", "approve", "confirm", "proceed", "ok", "go ahead"]):
            tool_info = self.approve_confirmation(session_id=session_id)
            return ("approved", tool_info)
        
        # Denial keywords
        if any(keyword in message_lower for keyword in ["no", "cancel", "deny", "stop", "don't"]):
            self.deny_confirmation(session_id=session_id)
            return ("denied", None)
        
        # Modification request (for future enhancement)
        if "modify" in message_lower or "change" in message_lower or "edit" in message_lower:
            return ("modify_requested", None)
        
        # Unclear response
        return ("unclear", None)
    
    def cleanup_expired(self):
        """Remove expired confirmations from memory."""
        expired_ids = [
            conf_id for conf_id, pending in self.pending_confirmations.items()
            if pending.is_expired()
        ]
        
        for conf_id in expired_ids:
            pending = self.pending_confirmations[conf_id]
            pending.status = "expired"
            # In production, you might want to keep these in a separate expired list
            # For now, we keep them but mark as expired
    
    def get_session_confirmations(self, session_id: str) -> list[PendingConfirmation]:
        """Get all confirmations for a session."""
        if session_id not in self.session_confirmations:
            return []
        
        return [
            self.pending_confirmations[conf_id]
            for conf_id in self.session_confirmations[session_id]
            if conf_id in self.pending_confirmations
        ]
    
    def clear_session(self, session_id: str):
        """Clear all confirmations for a session."""
        if session_id in self.session_confirmations:
            for conf_id in self.session_confirmations[session_id]:
                if conf_id in self.pending_confirmations:
                    del self.pending_confirmations[conf_id]
            del self.session_confirmations[session_id]


# Global confirmation handler instance
# In production, this should be replaced with a distributed store
_global_confirmation_handler = ToolConfirmationHandler()


def get_confirmation_handler() -> ToolConfirmationHandler:
    """Get the global confirmation handler instance."""
    return _global_confirmation_handler
