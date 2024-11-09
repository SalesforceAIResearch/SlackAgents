import json
import unittest
from unittest.mock import MagicMock, patch

from slackagents.agent.executor import Executor
from slackagents.llms.base import BaseLLM
from slackagents.tools.base import BaseTool
from slackagents.tools.function_tool import FunctionTool

class TestExecutor(unittest.TestCase):
    def setUp(self):
        # Create mock objects
        self.mock_llm = MagicMock(spec=BaseLLM)
        
        # Setup sample function tool
        def sample_function(arg1: str, arg2: int) -> str:
            """Test function for tools"""
            return f"Processed {arg1} with {arg2}"
        self.sample_tool = FunctionTool.from_function(sample_function)
        
        # Create default executor
        self.executor = Executor(
            name="test_executor",
            desc="test executor description",
            llm=self.mock_llm,
            tools=[self.sample_tool],
            max_steps=10,
            verbose=False
        )

    def test_initialization(self):
        """Test executor initialization"""
        self.assertEqual(self.executor.name, "test_executor")
        self.assertEqual(len(self.executor.messages), 1)  # System prompt
        self.assertEqual(len(self.executor.tools), 1)
        self.assertEqual(self.executor.max_steps, 10)

    def test_add_message(self):
        """Test adding messages to executor"""
        test_message = {"role": "user", "content": "test message"}
        self.executor.add_message(test_message)
        self.assertEqual(len(self.executor.messages), 2)
        self.assertEqual(self.executor.messages[-1], test_message)

    def test_add_tool(self):
        """Test adding new tool to executor"""
        new_mock_tool = MagicMock(spec=BaseTool)
        new_mock_tool.info = {"function": {"name": "new_tool"}}
        self.executor.add_tool(new_mock_tool)
        self.assertEqual(len(self.executor.tools), 2)
        self.assertIn("new_tool", self.executor.tool_name_to_tool)

    def test_step_without_tool_calls(self):
        """Test step method when LLM returns response without tool calls"""
        self.mock_llm.chat_completion.return_value = {
            "content": "Simple response"
        }
        message = self.executor.step()
        self.assertEqual(message["role"], "assistant")
        self.assertEqual(message["content"], "Simple response")

    def test_step_with_tool_calls(self):
        """Test step method when LLM returns response with tool calls"""
        tool_call = {
            "tool_calls": [{
                "id": "call_123",
                "function": {
                    "name": "sample_function",
                    "arguments": json.dumps({"arg1": "test", "arg2": 42})
                }
            }]
        }
        self.mock_llm.chat_completion.return_value = tool_call
        message = self.executor.step()
        self.assertEqual(message["role"], "assistant")
        self.assertIn("tool_calls", message)

    def test_execute_with_tool_calls(self):
        """Test execute method with tool calls"""
        # Setup mock responses
        tool_call_request = {
            "tool_calls": [{
                "id": "call_123",
                "function": {
                    "name": "sample_function",
                    "arguments": json.dumps({"arg1": "test", "arg2": 42})
                }
            }]
        }
                
        # Trigger transition to new module
        self.mock_llm.chat_completion.side_effect = [
            tool_call_request,
            {"content": "Done"}
        ]

        # Execute
        message = self.executor.execute()
        # Verify final response
        self.assertEqual(message["content"], "Done")
        # Verify intermediate messages
        self.assertEqual(len(self.executor.messages), 4)
        self.assertEqual(self.executor.messages[-2]["content"], "Processed test with 42")
        self.assertEqual(self.executor.messages[-1]["content"], "Done")
        self.assertNotIn("tool_calls", self.executor.messages[-1])

if __name__ == "__main__":
    unittest.main() 