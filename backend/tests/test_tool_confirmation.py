"""
Unit tests for Tool Confirmation System

Tests the confirmation configuration, handler, and integration with chat flow.
"""

import pytest
from datetime import datetime, timedelta
from my_app.server.tool_confirmation_config import (
    requires_confirmation,
    get_confirmation_rule,
    format_confirmation_message,
    TOOLS_REQUIRING_CONFIRMATION,
    add_confirmation_requirement,
    remove_confirmation_requirement,
    ToolConfirmationRule
)
from my_app.server.tool_confirmation_handler import (
    ToolConfirmationHandler,
    PendingConfirmation
)


class TestToolConfirmationConfig:
    """Test the configuration module."""
    
    def test_requires_confirmation_for_high_risk_tools(self):
        """High-risk tools should require confirmation."""
        assert requires_confirmation("createSalesforceCase") is True
        assert requires_confirmation("createSalesforceContact") is True
        assert requires_confirmation("sendSMS") is True
    
    def test_no_confirmation_for_unknown_tools(self):
        """Unknown tools should not require confirmation."""
        assert requires_confirmation("unknownTool123") is False
    
    def test_get_confirmation_rule(self):
        """Should retrieve correct confirmation rule."""
        rule = get_confirmation_rule("sendSMS")
        assert rule is not None
        assert rule.tool_name == "sendSMS"
        assert rule.risk_level == "medium"
    
    def test_format_confirmation_message(self):
        """Should format confirmation messages with tool args."""
        tool_args = {
            "phone_number": "+1234567890",
            "message": "Test message"
        }
        
        message = format_confirmation_message("sendSMS", tool_args)
        
        assert "sendSMS" in message.lower() or "sms" in message.lower()
        assert "+1234567890" in message
        assert "Test message" in message
        assert "yes" in message.lower() or "approve" in message.lower()
    
    def test_format_confirmation_with_missing_args(self):
        """Should handle missing arguments gracefully."""
        tool_args = {"phone_number": "+1234567890"}  # missing 'message'
        
        message = format_confirmation_message("sendSMS", tool_args)
        
        # Should not crash and should contain available info
        assert "+1234567890" in message
        assert "N/A" in message or message  # Should have fallback
    
    def test_add_confirmation_requirement(self):
        """Should allow adding new confirmation requirements."""
        new_rule = ToolConfirmationRule(
            tool_name="testTool",
            confirmation_message_template="Test: {param}",
            risk_level="low"
        )
        
        add_confirmation_requirement(new_rule)
        
        assert requires_confirmation("testTool") is True
        assert get_confirmation_rule("testTool") == new_rule
        
        # Cleanup
        remove_confirmation_requirement("testTool")
    
    def test_remove_confirmation_requirement(self):
        """Should allow removing confirmation requirements."""
        # Add a temporary rule
        test_rule = ToolConfirmationRule(
            tool_name="tempTool",
            confirmation_message_template="Temp",
            risk_level="low"
        )
        add_confirmation_requirement(test_rule)
        
        # Remove it
        remove_confirmation_requirement("tempTool")
        
        assert requires_confirmation("tempTool") is False


class TestToolConfirmationHandler:
    """Test the confirmation handler."""
    
    @pytest.fixture
    def handler(self):
        """Create a fresh handler for each test."""
        return ToolConfirmationHandler(confirmation_timeout_seconds=300)
    
    def test_create_confirmation_request(self, handler):
        """Should create a pending confirmation."""
        tool_name = "sendSMS"
        tool_args = {"phone_number": "+1234567890", "message": "Test"}
        
        conf_id, message = handler.create_confirmation_request(
            tool_name=tool_name,
            tool_args=tool_args,
            session_id="test-session"
        )
        
        assert conf_id is not None
        assert len(message) > 0
        assert "sms" in message.lower() or "message" in message.lower()
        
        # Should be able to retrieve it
        pending = handler.get_pending_confirmation(session_id="test-session")
        assert pending is not None
        assert pending.tool_name == tool_name
        assert pending.status == "pending"
    
    def test_approve_confirmation(self, handler):
        """Should approve a pending confirmation."""
        conf_id, _ = handler.create_confirmation_request(
            tool_name="sendSMS",
            tool_args={"phone_number": "+1234567890", "message": "Test"},
            session_id="test-session"
        )
        
        result = handler.approve_confirmation(session_id="test-session")
        
        assert result is not None
        tool_name, tool_args = result
        assert tool_name == "sendSMS"
        assert tool_args["phone_number"] == "+1234567890"
    
    def test_deny_confirmation(self, handler):
        """Should deny a pending confirmation."""
        handler.create_confirmation_request(
            tool_name="sendSMS",
            tool_args={"phone_number": "+1234567890", "message": "Test"},
            session_id="test-session"
        )
        
        result = handler.deny_confirmation(session_id="test-session")
        
        assert result is True
        
        # Should not be able to approve after denying
        approval = handler.approve_confirmation(session_id="test-session")
        assert approval is None
    
    def test_process_user_response_approval(self, handler):
        """Should recognize approval responses."""
        handler.create_confirmation_request(
            tool_name="sendSMS",
            tool_args={"phone_number": "+1234567890", "message": "Test"},
            session_id="test-session"
        )
        
        approval_phrases = ["yes", "YES", "approve", "confirm", "ok", "proceed"]
        
        for phrase in approval_phrases:
            # Create new confirmation for each test
            handler.create_confirmation_request(
                tool_name="sendSMS",
                tool_args={"phone": "+1234567890"},
                session_id=f"session-{phrase}"
            )
            
            response_type, tool_info = handler.process_user_response(
                phrase,
                session_id=f"session-{phrase}"
            )
            
            assert response_type == "approved", f"Failed for phrase: {phrase}"
            assert tool_info is not None
    
    def test_process_user_response_denial(self, handler):
        """Should recognize denial responses."""
        handler.create_confirmation_request(
            tool_name="sendSMS",
            tool_args={"phone_number": "+1234567890", "message": "Test"},
            session_id="test-session"
        )
        
        denial_phrases = ["no", "NO", "cancel", "deny", "stop"]
        
        for phrase in denial_phrases:
            # Create new confirmation for each test
            handler.create_confirmation_request(
                tool_name="sendSMS",
                tool_args={"phone": "+1234567890"},
                session_id=f"session-{phrase}"
            )
            
            response_type, _ = handler.process_user_response(
                phrase,
                session_id=f"session-{phrase}"
            )
            
            assert response_type == "denied", f"Failed for phrase: {phrase}"
    
    def test_process_user_response_no_pending(self, handler):
        """Should handle responses when no confirmation is pending."""
        response_type, tool_info = handler.process_user_response(
            "yes",
            session_id="nonexistent-session"
        )
        
        assert response_type == "no_pending"
        assert tool_info is None
    
    def test_confirmation_expiration(self, handler):
        """Should mark confirmations as expired after timeout."""
        # Create handler with very short timeout
        short_handler = ToolConfirmationHandler(confirmation_timeout_seconds=0)
        
        short_handler.create_confirmation_request(
            tool_name="sendSMS",
            tool_args={"phone_number": "+1234567890", "message": "Test"},
            session_id="test-session"
        )
        
        # Try to approve after timeout
        import time
        time.sleep(0.1)  # Wait a bit
        
        response_type, _ = short_handler.process_user_response(
            "yes",
            session_id="test-session"
        )
        
        # Should be expired
        assert response_type == "expired"
    
    def test_get_session_confirmations(self, handler):
        """Should retrieve all confirmations for a session."""
        session_id = "multi-conf-session"
        
        # Create multiple confirmations
        handler.create_confirmation_request(
            tool_name="sendSMS",
            tool_args={"phone": "+1111111111"},
            session_id=session_id
        )
        handler.create_confirmation_request(
            tool_name="sendVoiceCall",
            tool_args={"phone": "+2222222222"},
            session_id=session_id
        )
        
        confirmations = handler.get_session_confirmations(session_id)
        
        assert len(confirmations) == 2
        assert confirmations[0].tool_name in ["sendSMS", "sendVoiceCall"]
        assert confirmations[1].tool_name in ["sendSMS", "sendVoiceCall"]
    
    def test_clear_session(self, handler):
        """Should clear all confirmations for a session."""
        session_id = "clear-test-session"
        
        handler.create_confirmation_request(
            tool_name="sendSMS",
            tool_args={"phone": "+1234567890"},
            session_id=session_id
        )
        
        handler.clear_session(session_id)
        
        confirmations = handler.get_session_confirmations(session_id)
        assert len(confirmations) == 0


class TestConfirmationIntegration:
    """Test integration scenarios."""
    
    def test_full_workflow(self):
        """Test complete confirmation workflow."""
        handler = ToolConfirmationHandler()
        session_id = "integration-test"
        
        # 1. User requests action requiring confirmation
        tool_name = "createSalesforceContact"
        tool_args = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com"
        }
        
        # 2. System creates confirmation request
        conf_id, message = handler.create_confirmation_request(
            tool_name=tool_name,
            tool_args=tool_args,
            session_id=session_id
        )
        
        assert "John" in message
        assert "Doe" in message
        assert "john@example.com" in message
        
        # 3. User approves
        response_type, tool_info = handler.process_user_response(
            "yes, proceed",
            session_id=session_id
        )
        
        assert response_type == "approved"
        assert tool_info is not None
        
        returned_tool_name, returned_args = tool_info
        assert returned_tool_name == tool_name
        assert returned_args == tool_args
    
    def test_multiple_tools_different_sessions(self):
        """Test handling confirmations across different sessions."""
        handler = ToolConfirmationHandler()
        
        # Session 1
        handler.create_confirmation_request(
            tool_name="sendSMS",
            tool_args={"phone": "+1111111111"},
            session_id="session-1"
        )
        
        # Session 2
        handler.create_confirmation_request(
            tool_name="sendVoiceCall",
            tool_args={"phone": "+2222222222"},
            session_id="session-2"
        )
        
        # Approve session 1
        response_type1, tool_info1 = handler.process_user_response(
            "yes",
            session_id="session-1"
        )
        
        # Deny session 2
        response_type2, tool_info2 = handler.process_user_response(
            "no",
            session_id="session-2"
        )
        
        assert response_type1 == "approved"
        assert tool_info1[0] == "sendSMS"
        
        assert response_type2 == "denied"
        assert tool_info2 is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
