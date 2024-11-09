BASE_ASSISTANT_PROMPT = """
You are a helpful assistant.
""".strip()

TRANSITION_PROMPT_TEMPLATE = """
You are a helpful assistant. You can continue the execution or transit to other modules.

Current Module:
{current_module}
""".strip()

SLACK_ASSISTANT_PROMPT = """
You are a helpful assistant. You can send a message to your colleagues or respond to the message sender.
""".strip()

SLACK_COLLEAGUES_PROMPT = """
#Colleagues:
{colleagues}
""".strip()

BASE_ASSISTANT_DESCRIPTION = """
You are a helpful assistant.
""".strip()

BASE_ASSISTANT_NAME = "Assistant"