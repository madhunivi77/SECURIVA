import unittest

from my_app.server.grounded_chat_policy import GROUNDING_SYSTEM_PROMPT, prepare_messages_for_agent


class GroundedChatPolicyTests(unittest.TestCase):
    def test_adds_grounding_prompt_for_explanation_request(self):
        original_messages = [{"role": "user", "content": "Explain why we should encrypt customer data"}]

        prepared_messages = prepare_messages_for_agent(original_messages)

        self.assertEqual(original_messages, [{"role": "user", "content": "Explain why we should encrypt customer data"}])
        self.assertEqual(prepared_messages[0]["role"], "system")
        self.assertEqual(prepared_messages[0]["content"], GROUNDING_SYSTEM_PROMPT)
        self.assertEqual(prepared_messages[1]["content"], original_messages[0]["content"])

    def test_appends_grounding_prompt_to_existing_system_message(self):
        prepared_messages = prepare_messages_for_agent([
            {"role": "system", "content": "Base instructions"},
            {"role": "user", "content": "Can I share data with a vendor?"},
        ])

        self.assertTrue(prepared_messages[0]["content"].startswith("Base instructions"))
        self.assertIn(GROUNDING_SYSTEM_PROMPT, prepared_messages[0]["content"])

    def test_leaves_non_guidance_request_unchanged(self):
        messages = [{"role": "user", "content": "List the compliance tools available"}]

        prepared_messages = prepare_messages_for_agent(messages)

        self.assertEqual(prepared_messages, messages)


if __name__ == "__main__":
    unittest.main()