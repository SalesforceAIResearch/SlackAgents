import json
from slackagents.slack.handler import SlackDMHandler
from agent.slack_agent import video_search_agent

with open(".slack.config", "r") as config_file:
    BOLT_CONFIG = json.load(config_file)

if __name__ == "__main__":
    handler = SlackDMHandler(BOLT_CONFIG, video_search_agent)
    handler.run()