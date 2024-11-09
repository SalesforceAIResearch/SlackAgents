import json

from slackagents.tools.base import BaseTool
from slackagents.commons.prompts.send_message_function_prompt import SEND_MESSAGE_FUNCTION_TEMPLATE
from slackagents.commons.prompts.wait_function_prompt import WAIT_FUNCTION_TEMPLATE
from slackagents.commons.prompts.get_thread_history_function_prompt import GET_THREAD_HISTORY_FUNCTION_TEMPLATE
from slackagents.tools.utils import create_base_tool_from_json

send_message_tool = create_base_tool_from_json(json.loads(SEND_MESSAGE_FUNCTION_TEMPLATE.format()))
wait_tool = create_base_tool_from_json(json.loads(WAIT_FUNCTION_TEMPLATE.format()))
get_thread_history_tool = create_base_tool_from_json(json.loads(GET_THREAD_HISTORY_FUNCTION_TEMPLATE.format()))