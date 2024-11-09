from slackagents.agent.slack_assistant import SlackAssistant
from prompts.prompts import sales_agent_prompt
from tools.check_inventory import check_inventory_tool, get_low_stock_products_tool
from slackagents.tools.slack_agent_tools import get_thread_history_tool
from slack_bolt_id import sales_agent_bolt_config

agent_config = {    
    "name": "John",
    "desc": "John is a sales agent for an E-commerce company.",
    "system_prompt": sales_agent_prompt,
    "slack_bot_token": sales_agent_bolt_config["SLACK_BOT_TOKEN"],
    "tools": [check_inventory_tool, get_low_stock_products_tool, get_thread_history_tool],
    "colleagues": {
        "U071Y175CTT": {"name": "Jane", "desc": "Jane is a customer service agent for an E-commerce company."},
        "U0728DDNGQY": {"name": "Jack", "desc": "Jack is a logistics agent for an E-commerce company."}
    }
}

sales_agent = SlackAssistant(**agent_config)
