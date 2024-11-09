from typing import Any, Union
from slackagents.tools.base import FunctionDefinition, ToolCall, BaseTool
from slackagents.tools.function_tool import FunctionTool

# Import wrappers
from slackagents.tools.wrappers.llamaindex import LlamaIndexToolWrapper
from slackagents.tools.wrappers.langchain import LangChainToolWrapper
from slackagents.tools.wrappers.crewai import CrewAIToolWrapper
from slackagents.tools.wrappers.composio import ComposioToolWrapper

class SlackAgentsWrapper:
    """
    A unified wrapper for tools from LlamaIndex, LangChain, CrewAI, and Composio.
    """
    def __init__(self, tool: Any):
        """
        Initialize the SlackAgentsWrapper.

        :param tool: The tool to be wrapped (from LlamaIndex, LangChain, CrewAI, or Composio).
        :type tool: Any
        """
        self.wrapper = self._get_appropriate_wrapper(tool)
        self.name = self.wrapper.name
        self.function = self.wrapper.function
        self.tool = self.wrapper.tool

    def _get_appropriate_wrapper(self, tool: Any) -> Union[LlamaIndexToolWrapper, LangChainToolWrapper, CrewAIToolWrapper, ComposioToolWrapper]:
        """
        Determine the appropriate wrapper based on the tool type.

        :param tool: The tool to be wrapped.
        :type tool: Any
        :return: The appropriate wrapper instance.
        :rtype: Union[LlamaIndexToolWrapper, LangChainToolWrapper, CrewAIToolWrapper, ComposioToolWrapper]
        :raises ValueError: If the tool type is not recognized.
        """
        try:
            from llama_index.core.tools import FunctionTool as LlamaIndexFunctionTool
            if isinstance(tool, LlamaIndexFunctionTool):
                return LlamaIndexToolWrapper(tool)
        except ImportError:
            pass

        try:
            from langchain_core.tools import BaseTool as LangChainBaseTool
            if isinstance(tool, LangChainBaseTool):
                return LangChainToolWrapper(tool)
        except ImportError:
            pass

        try:
            from crewai_tools import BaseTool as CrewAITool
            if isinstance(tool, CrewAITool):
                return CrewAIToolWrapper(tool)
        except ImportError:
            pass

        try:
            from composio_openai import Action as ComposioAction
            if isinstance(tool, ComposioAction):
                return ComposioToolWrapper(tool)
        except ImportError:
            pass

        raise ValueError(f"Unsupported tool type: {type(tool)}")

    @property
    def info(self):
        """
        Get the information of the tool.

        :return: The function definition of the tool.
        :rtype: dict
        """
        return self.wrapper.info

    def execute(self, tool_call: ToolCall) -> Any:
        """
        Execute the tool's functionality.

        :param tool_call: The tool call to be executed.
        :type tool_call: ToolCall
        :return: The result of the tool execution.
        :rtype: Any
        """
        return self.wrapper.execute(tool_call)

