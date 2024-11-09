"""Base class for agent tools."""
import uuid
from typing import Dict, Any
from pydantic import BaseModel, Field
from slackagents.tools.schema import FunctionDefinition


class ToolCall(BaseModel):
    """Base class for tool calls."""
    id: str = Field(default_factory=uuid.uuid4)
    name: str
    arguments: Dict[str, Any]

    def __str__(self):
        return f"{self.name}({self.arguments})"


class BaseTool(BaseModel):
    """Base class for agent tools."""
    name: str = Field(
        default=None, 
        description="The tool's name"
    )
    
    function: FunctionDefinition = Field(
        default=None, 
        description="The tool's function definition in OpenAPI format with name, description, and parameters"
    )
    
    def __init__(self, name: str, function: FunctionDefinition):
        super().__init__(
            name=name, function=function
        )
    
    @property
    def info(self) -> Dict[str, Any]:
        """Return the tool's OpenAPI tool specification."""
        return {
            "type": "function",
            "function": self.function,
        }
    
    def execute(self,  *args: Any, **kwargs: Any) -> Any:
        """Execute the tool's functionality."""
        raise NotImplementedError

    def __str__(self):
        return str(self.info)
    
    def __repr__(self):
        return str(self.info)

if __name__ == "__main__": 
    name = "get_weather"
    description = "Get the weather for a given location"
    parameters = {
        "type": "object",
        "properties": {
            "order_id": {
                "type": "string",
                "description": "The customer's order ID.",
            },
        },
        "required": ["order_id"],
        "additionalProperties": False,
    }
    
    function = FunctionDefinition(
        name=name,
        description=description,
        parameters=parameters
    )
    
    tool = BaseTool(name, function)
    print(tool)
