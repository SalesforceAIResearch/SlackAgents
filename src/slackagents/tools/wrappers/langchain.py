from slackagents.tools.base import FunctionDefinition, ToolCall
from slackagents.tools.base import BaseTool
from typing import Any
try:
    from langchain_core.tools import BaseTool as LangChainBaseTool
    from langchain_core.utils.function_calling import convert_to_openai_function
except ImportError:
    raise ImportError("Please install the langchain-core package to use this wrapper. Run 'pip install langchain'")

class LangChainToolWrapper:
    def __init__(self, tool: LangChainBaseTool):
        self.langchain_tool = tool
        self.metadata = convert_to_openai_function(tool)
        self.name = self.metadata["name"]
        self.function = FunctionDefinition(
            name=self.metadata["name"],
            description=self.metadata["description"],
            parameters=self.metadata["parameters"]
        )
        self.tool = BaseTool(
            name=self.metadata["name"],
            function=self.function,
        )
    
    @property
    def info(self):
        return self.tool.info
    
    def execute(self, tool_call: ToolCall) -> Any:
        """Execute the tool's functionality."""
        func_args = tool_call.arguments
        return self.langchain_tool.run(func_args)