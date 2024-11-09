import unittest
from unittest.mock import Mock
from pydantic import BaseModel, Field
from typing import Optional

from slackagents.tools.function_tool import FunctionTool
from slackagents.tools.base import ToolCall

class TestFunctionTool(unittest.TestCase):

    def setUp(self):
        def sample_function(arg1: str, arg2: int = 5):
            """Sample function for testing.
            
            :param arg1: The first argument
            :param arg2: The second argument
            :return: The processed result
            """
            return f"Processed {arg1} with {arg2}"

        self.sample_function = sample_function

    def test_from_function(self):
        tool = FunctionTool.from_function(self.sample_function)
        self.assertEqual(tool.name, "sample_function")
        self.assertEqual(tool.function["name"], "sample_function")
        self.assertEqual(tool.function["description"], "Sample function for testing.")
        self.assertEqual(tool.function["parameters"]["properties"]["arg1"]["description"], "The first argument")
        self.assertEqual(tool.callback, self.sample_function)

    def test_execute_with_valid_args(self):
        tool = FunctionTool.from_function(self.sample_function)
        call = ToolCall(name="sample_function", arguments={"arg1": "test", "arg2": 10})
        
        result = tool.execute(call)
        self.assertEqual(result, "Processed test with 10")

    def test_execute_with_missing_required_arg(self):
        tool = FunctionTool.from_function(self.sample_function)
        call = ToolCall(name="sample_function", arguments={"arg2": 10})
        
        result = tool.execute(call)
        self.assertIn("error", result)
        self.assertIn("arg1", result["error"])

    def test_from_pydantic(self):
        class SampleModel(BaseModel):
            """A sample Pydantic model for testing."""
            arg1: str = Field(description="First argument")
            arg2: Optional[int] = Field(default=5, description="Second argument")

            @classmethod
            def execute(cls, arg1: str, arg2: int = 5):
                return f"Executed with {arg1} and {arg2}"

        tool = FunctionTool.from_pydantic(SampleModel, name="sample_model", description="Sample model tool")

        self.assertEqual(tool.name, "sample_model")
        self.assertEqual(tool.function["name"], "sample_model")
        self.assertEqual(tool.function["description"], "Sample model tool")
        self.assertEqual(tool.callback, SampleModel.execute)

    def test_execute_pydantic_tool(self):
        class SampleModel(BaseModel):
            """A sample Pydantic model for testing."""
            arg1: str = Field(description="First argument")
            arg2: Optional[int] = Field(default=5, description="Second argument")

            @classmethod
            def execute(cls, arg1: str, arg2: int = 5):
                return f"Executed with {arg1} and {arg2}"

        tool = FunctionTool.from_pydantic(SampleModel)
        call = ToolCall(name="SampleModel", arguments={"arg1": "test", "arg2": 10})

        result = tool.execute(call)
        self.assertEqual(result, "Executed with test and 10")

if __name__ == '__main__':
    unittest.main()