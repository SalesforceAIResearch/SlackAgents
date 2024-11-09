from dotenv import load_dotenv
load_dotenv()

import unittest
from unittest.mock import patch, MagicMock
from slackagents.agent.assistant import Assistant
from slackagents.llms.base import BaseLLM
from slackagents.tools.base import BaseTool
from slackagents.commons.default_prompts import BASE_ASSISTANT_PROMPT

class TestAssistant(unittest.TestCase):

    def setUp(self):
        self.mock_llm = MagicMock(spec=BaseLLM)
        self.mock_tool = MagicMock(spec=BaseTool)
        self.mock_tool.info = {"function": {"name": "mock_tool"}}
        self.assistant = Assistant(
            "Test Assistant", 
            "A test assistant", 
            llm=self.mock_llm, 
            tools=[self.mock_tool]
        )

    def test_initialization(self):
        self.assertEqual(self.assistant.name, "Test Assistant")
        self.assertEqual(self.assistant.desc, "A test assistant")
        self.assertEqual(len(self.assistant.messages), 1)
        self.assertEqual(self.assistant.messages[0]["role"], "system")
        self.assertEqual(self.assistant.messages[0]["content"], BASE_ASSISTANT_PROMPT)

    def test_chat_without_tool_calls(self):
        self.mock_llm.chat_completion.return_value = {
            "content": "Test response",
            "tool_calls": None
        }
        
        response = self.assistant.chat("Test message")
        
        self.assertEqual(response, "Test response")
        self.assertEqual(len(self.assistant.messages), 3)
        self.mock_llm.chat_completion.assert_called_once()

    def test_chat_with_tool_calls(self):
        # First response includes a tool call
        self.mock_llm.chat_completion.side_effect = [
            {
                "tool_calls": [
                    {
                        "function": {"name": "mock_tool", "arguments": "{}"},
                        "id": "123"
                    }
                ],
                "content": None
            },
            {
                "content": "Final response",
                "tool_calls": None
            }
        ]
        
        self.mock_tool.execute.return_value = "Tool output"
        response = self.assistant.chat("Test message")
        
        self.assertEqual(response, "Final response")
        self.assertEqual(len(self.assistant.messages), 5)
        self.assertEqual(self.mock_llm.chat_completion.call_count, 2)

    def test_chat_with_multiple_tool_calls(self):
        self.mock_llm.chat_completion.side_effect = [
            {
                "tool_calls": [
                    {
                        "function": {"name": "mock_tool", "arguments": "{}"},
                        "id": "123"
                    },
                    {
                        "function": {"name": "mock_tool", "arguments": '{"param": "value"}'},
                        "id": "456"
                    }
                ],
                "content": None
            },
            {
                "content": "Final response",
                "tool_calls": None
            }
        ]
        
        self.mock_tool.execute.side_effect = ["Tool output 1", "Tool output 2"]
        response = self.assistant.chat("Test message")
        
        self.assertEqual(response, "Final response")
        self.assertEqual(len(self.assistant.messages), 6)  # system + user + 1 parallel tool call + 2 tool results + final response
        self.assertEqual(self.mock_tool.execute.call_count, 2)

if __name__ == '__main__':
    unittest.main()