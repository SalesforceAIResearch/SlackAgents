try:
    from crewai_tools import BaseTool as CrewAITool
except ImportError:
    raise ImportError("Please install the crewai-tools package to use this wrapper. Run pip install 'crewai[tools]'")
from slackagents.tools.function_tool import FunctionTool
from slackagents.tools.base import ToolCall, FunctionDefinition
from typing import Any

class CrewAIToolWrapper:
    def __init__(self, tool: CrewAITool):
        self.crewai_tool = tool
        self.name = tool.name
        self.function = FunctionDefinition(
            name=self.name,
            description=tool.description,
            parameters=tool.args_schema.schema()
        )
        self.tool = FunctionTool(
            name=self.name,
            function=self.function,
            callback=self.crewai_tool._run
        )

    @property
    def info(self):
        return self.tool.info
    
    def execute(self, tool_call: ToolCall) -> Any:
        """Execute the tool's functionality."""
        return self.tool.execute(tool_call)