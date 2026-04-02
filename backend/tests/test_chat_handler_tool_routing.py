import unittest

from my_app.server.chat_handler import (
    classify_tool_route,
    filter_mcp_tools_for_route,
    get_latest_user_message_content,
)


class FakeTool:
    def __init__(self, name: str):
        self.name = name


class ChatHandlerToolRoutingTests(unittest.TestCase):
    def test_get_latest_user_message_content_returns_last_user_message(self):
        messages = [
            {"role": "user", "content": "First question"},
            {"role": "assistant", "content": "Reply"},
            {"role": "user", "content": "Latest question"},
        ]

        result = get_latest_user_message_content(messages)

        self.assertEqual(result, "Latest question")

    def test_classify_tool_route_uses_grounded_guidance_for_how_to_questions(self):
        route = classify_tool_route([
            {"role": "user", "content": "How do I handle a GDPR deletion request?"}
        ])

        self.assertEqual(route, "grounded_guidance")

    def test_classify_tool_route_uses_compliance_reference_for_lookup_questions(self):
        route = classify_tool_route([
            {"role": "user", "content": "What are the GDPR breach notification requirements?"}
        ])

        self.assertEqual(route, "compliance_reference")

    def test_classify_tool_route_uses_compliance_report_for_report_generation(self):
        route = classify_tool_route([
            {"role": "user", "content": "Generate a GDPR and HIPAA compliance report with penalties"}
        ])

        self.assertEqual(route, "compliance_report")

    def test_classify_tool_route_leaves_non_compliance_requests_on_default_path(self):
        route = classify_tool_route([
            {"role": "user", "content": "Create a Salesforce case for this outage"}
        ])

        self.assertEqual(route, "default")

    def test_filter_mcp_tools_for_grounded_guidance_removes_unrelated_tools(self):
        tools = [
            FakeTool("getGroundedSecurityGuidance"),
            FakeTool("getComplianceRequirements"),
            FakeTool("createSalesforceCase"),
            FakeTool("sendSMS"),
        ]

        filtered_tools = filter_mcp_tools_for_route(tools, "grounded_guidance")

        self.assertEqual(
            [tool.name for tool in filtered_tools],
            ["getGroundedSecurityGuidance", "getComplianceRequirements"],
        )

    def test_filter_mcp_tools_for_report_route_keeps_confirmation_tools(self):
        tools = [
            FakeTool("generateComplianceReport"),
            FakeTool("confirmComplianceUnderstanding"),
            FakeTool("validateComplianceParameters"),
            FakeTool("createSalesforceCase"),
        ]

        filtered_tools = filter_mcp_tools_for_route(tools, "compliance_report")

        self.assertEqual(
            [tool.name for tool in filtered_tools],
            [
                "generateComplianceReport",
                "confirmComplianceUnderstanding",
                "validateComplianceParameters",
            ],
        )

    def test_filter_mcp_tools_falls_back_to_full_set_when_allowlist_missing(self):
        tools = [FakeTool("createSalesforceCase"), FakeTool("sendSMS")]

        filtered_tools = filter_mcp_tools_for_route(tools, "grounded_guidance")

        self.assertEqual(filtered_tools, tools)


if __name__ == "__main__":
    unittest.main()