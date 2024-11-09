from slackagents.agent.slack_assistant import SlackAssistant
from slackagents.tools.slack_agent_tools import get_thread_history_tool
from slack_bolt_id import customer_service_bolt_config
from prompts.prompts import customer_service_agent_prompt

agent_config = {
    "name": "Jane",
    "desc": "CustomerServiceAgent is a customer service agent for an E-commerce company.",
    "system_prompt": customer_service_agent_prompt,
    "tools": [get_thread_history_tool],
    "slack_bot_token": customer_service_bolt_config["SLACK_BOT_TOKEN"],
    "colleagues": {
        "U071Y175CTT": {"name": "Jack", "desc": "Jack is a logistics agent for an E-commerce company."},
        "U0728DDNGQY": {"name": "John", "desc": "John is a sales agent for an E-commerce company."}
    }
}

customer_service_agent = SlackAssistant(**agent_config)
