from slackagents.tools.base import BaseTool, FunctionDefinition, ToolCall
from slackagents.tools.utils import generate_function_definition_from_callable, auto_cast_params
from typing import Any, Callable, Optional
from pydantic import BaseModel, Field
import openai
import json

class FunctionTool(BaseTool):
    """Class for function calling tools."""
    callback: Callable = Field(
        default=None, description="The function callable to execute."
    )
    
    def __init__(self, name: str, function: FunctionDefinition, callback: Callable):
        super().__init__(name=name, function=function)
        self.callback = callback
    
    @classmethod
    def from_function(cls, function: Callable):
        """Create a new function tool from a function."""
        try:
            function_definition = generate_function_definition_from_callable(function)
        except Exception as e:
            function_definition = {
                "name": function.__name__,
                "description": function.__doc__,
            }
            import warnings
            warnings.warn(f"Failed to generate function definition for {function.__name__}: {str(e)}. Using raw docstring.")
        
        return cls(
            name=function.__name__, 
            function=function_definition, 
            callback=function
        )

    @classmethod
    def from_pydantic(cls, model, name: str = None, description: str = None):
        """Create a new structured tool from a Pydantic model."""
        if name is None:
            name = model.__name__
        if description is None:
            description = model.__doc__
        pydantic_function_tool = openai.pydantic_function_tool(
            model, name=name, description=description
        )
        function_definition = pydantic_function_tool["function"]
        return cls(
            name=name, 
            function=function_definition, 
            callback=model.execute
        )
        
    def execute(self, tool_call: ToolCall) -> Any:
        """Execute the tool's functionality."""
        func_args = tool_call.arguments
        # Execute the function with exception handling
        try:
            # Automatically cast the LLM generated parameters to the correct types
            output = auto_cast_params(self.callback, **func_args)
            if isinstance(output, str):
                return output
            else:
                # Convert the output to a string based on its type
                if isinstance(output, (list, dict)):
                    return json.dumps(output)
                elif isinstance(output, (int, float, bool)):
                    return str(output)
                else:
                    return repr(output)
        except Exception as e:
            return {"error": str(e)}

if __name__ == "__main__":
    # Initialize from function
    def arxiv_search(query: str, max_results: int = 5):
        """Search arXiv for papers matching the query.
        :param query: The search query.
        :param max_results: The maximum number of results to return.
        """
        return f"Searching arXiv for papers matching '{query}' with a maximum of {max_results} results."
    
    call = ToolCall(name="arxiv_search", arguments={"query": "quantum computing"})
    arxiv_search_tool = FunctionTool.from_function(arxiv_search)
    print(arxiv_search_tool.info)
    print(arxiv_search_tool.execute(call))
    
    # Initialize from Pydantic model
    class ArxivSearchTool(BaseModel):
        """A Pydantic model for arXiv search queries."""
        query: str = Field(
            default=None, 
            description="The search query."
        )
        max_results: Optional[int] = Field(
            default=5, 
            description="The maximum number of results to return."
        )
        
        @classmethod
        def execute(cls, query: str, max_results: int = 5):
            return arxiv_search(query, max_results)
    
    arxiv_search_tool = FunctionTool.from_pydantic(
        ArxivSearchTool, 
        name="arxiv_search", 
        description="Search arXiv for papers matching the query."
    )
    print(arxiv_search_tool.info)
    print(arxiv_search_tool.execute(call))