from slack_bolt_id import BOLT_CONFIG
from slackagents.commons.default_prompts import BASE_ASSISTANT_PROMPT
from slackagents.slack.handler import SlackDMHandler
from slackagents.agent.slack_dm_agent import SlackDMAgent


if __name__ == "__main__":
    agent_config = {
        "name": "MyAgent",
        "desc": "MyAgent is a simple assistant that can chat with users in Slack",
        "system_prompt": "You are a helpful assistant that can answer questions and help with tasks",
        "max_steps": 10
    }
    assistant = SlackDMAgent(**agent_config)
    handler = SlackDMHandler(BOLT_CONFIG, assistant)
    handler.run()
