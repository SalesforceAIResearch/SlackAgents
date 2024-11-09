from typing import Any
try:
    from composio_openai import ComposioToolSet
    from composio_openai import Action as ComposioAction
except ImportError:
    raise ImportError("Please install the composio-openai package to use this wrapper. Run pip install 'composio-openai'")
from slackagents.tools.base import FunctionDefinition, ToolCall, BaseTool

from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())

class ComposioToolWrapper:
    def __init__(self, action: ComposioAction):
        """
        Initialize the ComposioToolWrapper.

        :param action: The Composio action to be wrapped.
        :type action: ComposioAction
        """
        self.composio_toolset = ComposioToolSet(api_key=os.getenv("COMPOSIO_API_KEY"))        
        self.composio_tool = self.composio_toolset.get_tools(actions=[action])[0]   
        self.name = self.composio_tool["function"]["name"]
        self.function = FunctionDefinition(
            name=self.name,
            description=self.composio_tool["function"]["description"],
            parameters=self.composio_tool["function"]["parameters"]
        )
        self.tool = BaseTool(
            name=self.name,
            function=self.function,
        )

    @property
    def info(self):
        return self.tool.info
    
    def execute(self, tool_call: ToolCall) -> Any:
        """Execute the tool's functionality."""
        return self.composio_toolset.execute_action(
            action=ComposioAction(value=self.name),
            params=tool_call.arguments
        )