from slackagents.slack.utils import delete_channel_history
from slack_bolt_id import BOLT_CONFIG

if __name__ == "__main__":
    delete_channel_history(channel_id="D071535JDK9", bot_token=BOLT_CONFIG["SLACK_BOT_TOKEN"])
