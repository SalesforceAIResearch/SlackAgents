import unittest
from slackagents.tools.base import BaseTool
from slackagents.tools.schema import FunctionDefinition

class TestBaseTool(unittest.TestCase):
    def setUp(self):
        self.name = "get_weather"
        self.description = "Get the weather for a given location"
        self.parameters = {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The location to get weather for.",
                },
            },
            "required": ["location"],
            "additionalProperties": False,
        }
        self.function = FunctionDefinition(
            name=self.name,
            description=self.description,
            parameters=self.parameters
        )
        self.tool = BaseTool(name=self.name, function=self.function)

    def test_base_tool_initialization(self):
        self.assertEqual(self.tool.name, self.name)
        self.assertEqual(self.tool.function, self.function)

    def test_base_tool_info_property(self):
        expected_info = {
            "type": "function",
            "function": self.function,
        }
        self.assertEqual(self.tool.info, expected_info)

    def test_base_tool_execute_method(self):
        with self.assertRaises(NotImplementedError):
            self.tool.execute()

    def test_base_tool_str_representation(self):
        expected_str = str(self.tool.info)
        self.assertEqual(str(self.tool), expected_str)

    def test_base_tool_repr_representation(self):
        expected_repr = str(self.tool.info)
        self.assertEqual(repr(self.tool), expected_repr)

if __name__ == '__main__':
    unittest.main()