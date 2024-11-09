from slackagents.commons.default_prompts import SLACK_ASSISTANT_PROMPT
from slackagents.slack.handler import SlackChannelHandler
from slackagents.agent.slack_assistant import SlackAssistant
from slack_bolt_id import BOLT_CONFIG
from slackagents.slack.utils import get_channel_user_ids_and_names
from slackagents.slack.slack_agent_runner import SlackAppAgentRunner

if __name__ == "__main__":
    agent_config = {
        "name": "SimpleOAI",
        "desc": "SimpleOAI is a simple assistant that can chat with users in Slack",
        "tools": [],
        "system_prompt": SLACK_ASSISTANT_PROMPT,
        "max_steps": 10,
        "slack_bot_token": BOLT_CONFIG["SLACK_BOT_TOKEN"],
        "colleagues": {
            "U0706S5BYE8": {"name": "Customer", "description": "Customer"}, 
            "U07L0S04V35": {"name": "Logistic Agent", "description": "Logistic Agent"}
        }
    }
    agent = SlackAssistant(**agent_config)
    handler = SlackAppAgentRunner(BOLT_CONFIG, agent_config, agent_config)
    handler.run()
