from slackagents import FunctionTool
from .code_interpreter import code_interpreter
from .google_search import google_search
# Step 1: Convert the function to a tool
code_interpreter = FunctionTool.from_function(code_interpreter)
google_search = FunctionTool.from_function(google_search)
# Step 2: Export the tool
__all__ = ["code_interpreter", "google_search"]
