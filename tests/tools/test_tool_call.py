import unittest
from uuid import UUID
from slackagents.tools.base import ToolCall

class TestToolCall(unittest.TestCase):
    def setUp(self):
        self.name = "test_tool"
        self.arguments = {"arg1": "value1", "arg2": 42}
        self.tool_call = ToolCall(name=self.name, arguments=self.arguments)

    def test_tool_call_initialization(self):
        self.assertEqual(self.tool_call.name, self.name)
        self.assertEqual(self.tool_call.arguments, self.arguments)
        self.assertIsInstance(self.tool_call.id, UUID)

    def test_tool_call_str_representation(self):
        expected_str = f"{self.name}({self.arguments})"
        self.assertEqual(str(self.tool_call), expected_str)

if __name__ == '__main__':
    unittest.main()