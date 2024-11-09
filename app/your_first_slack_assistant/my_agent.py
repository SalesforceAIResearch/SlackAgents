from slackagents.commons.default_prompts import BASE_ASSISTANT_PROMPT
from slackagents.slack.handler import SlackDMHandler
from slackagents.agent.slack_dm_agent import SlackDMAgent
import json

if __name__ == "__main__":
    with open("agent_config.json", "r") as f:
        agent_config = json.load(f)
    with open("slack_bolt_id.json", "r") as f:
        bolt_config = json.load(f)
    assistant = SlackDMAgent(**agent_config)
    handler = SlackDMHandler(bolt_config, assistant)
    handler.run()