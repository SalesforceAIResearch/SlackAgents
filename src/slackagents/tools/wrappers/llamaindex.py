from slackagents.tools.base import FunctionDefinition, ToolCall
from slackagents.tools.function_tool import FunctionTool
from typing import Any

try:
    from llama_index.core.tools import FunctionTool as LlamaIndexFunctionTool
except ImportError:
    raise ImportError("Please install the llama_index package to use this wrapper. Run 'pip install llama_index'")

class LlamaIndexToolWrapper:
    """
    A wrapper for the LlamaIndex tool to be used in the ToolAssistant.
    """
    def __init__(self, tool: LlamaIndexFunctionTool):
        """
        Initialize the LlamaIndexToolWrapper.

        :param tool: The LlamaIndex tool to be wrapped.
        :type tool: llama_index.core.tools.FunctionTool
        :return: None
        :rtype: None
        """
        self.llamaindex_tool = tool
        self.metadata = self.llamaindex_tool.metadata.to_openai_tool()
        self.name = self.metadata["function"]["name"]
        self.function = FunctionDefinition(
            name=self.metadata["function"]["name"],
            description=self.metadata["function"]["description"],
            parameters=self.metadata["function"]["parameters"]
        )
        self.tool = FunctionTool(
            name=self.metadata["function"]["name"],
            function=self.function,
            callback=self.llamaindex_tool.fn
        )
    
    @property
    def info(self):
        """
        Get the information of the tool.

        :return: The function definition of the tool.
        :rtype: dict
        """
        return self.tool.info
    
    def execute(self, tool_call: ToolCall) -> Any:
        """
        Execute the tool's functionality.

        :param tool_call: The tool call to be executed.
        :type tool_call: ToolCall
        :return: The result of the tool execution.
        :rtype: Any
        """
        return self.tool.execute(tool_call)