from slackagents import FunctionTool
from .load_employee_calendar_tool import load_employee_calendar_tool
from .send_calendar_invite_tool import send_calendar_invite_tool
from .send_email_tool import send_email_tool
from .write_to_markdown_file import write_tool
from .load_jira_record_tool import load_jira_record_tool

# Step 1: Define the tools
load_employee_calendar_tool = FunctionTool.from_function(load_employee_calendar_tool)
send_calendar_invite_tool = FunctionTool.from_function(send_calendar_invite_tool)
send_email_tool = FunctionTool.from_function(send_email_tool)
write_tool = FunctionTool.from_function(write_tool)
load_jira_record_tool = FunctionTool.from_function(load_jira_record_tool)

# Step 2: Export the tools
__all__ = [
    "load_employee_calendar_tool",
    "send_calendar_invite_tool",
    "send_email_tool",
    "write_tool",
    "load_jira_record_tool",
]