from slackagents.agent.slack_assistant import SlackAssistant
from prompts.prompts import logistics_agent_prompt
from tools.check_order_status import check_order_status_tool
from slackagents.tools.slack_agent_tools import get_thread_history_tool
from slack_bolt_id import logistics_bolt_config

agent_config = {
    "name": "Jack",
    "desc": "Jack is a logistics agent for an E-commerce company.",
    "system_prompt": logistics_agent_prompt,
    "tools": [check_order_status_tool, get_thread_history_tool],
    "slack_bot_token": logistics_bolt_config["SLACK_BOT_TOKEN"],
    "colleagues": {
        "U0728DDNGQY": {"name": "John", "desc": "John is a sales agent for an E-commerce company."},
        "U071Y175CTT": {"name": "Jane", "desc": "Jane is a customer service agent for an E-commerce company."}
    }
}

logistics_agent = SlackAssistant(**agent_config)
