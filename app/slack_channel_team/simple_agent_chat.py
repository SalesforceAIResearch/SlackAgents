from slackagents.commons.default_prompts import SLACK_ASSISTANT_PROMPT
from slackagents.slack.handler import SlackChannelHandler
from slackagents.agent.slack_assistant import SlackAssistant
from slack_bolt_id import BOLT_CONFIG
from slackagents.slack.utils import get_channel_user_ids_and_names


if __name__ == "__main__":
    agent_config = {
        "name": "MyAgent",
        "desc": "MyAgent is a simple assistant that can chat with users in Slack",
        "system_prompt": "You are a helpful assistant that can answer questions and help with tasks",
        "tool_choice": "required",
        "max_steps": 10,
        "slack_bot_token": BOLT_CONFIG["SLACK_BOT_TOKEN"],
        "colleagues": {
            "U0706S5BYE8": {"name": "Customer", "description": "Customer"}, 
            "U07L0S04V35": {"name": "Logistic Agent", "description": "Logistic Agent"}
        }
    }
    agent = SlackAssistant(**agent_config)
    handler = SlackChannelHandler(BOLT_CONFIG, agent)
    handler.run()
