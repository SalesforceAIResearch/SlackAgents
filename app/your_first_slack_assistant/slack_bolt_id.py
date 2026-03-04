import os

# Load from environment to avoid committing secrets. Set SLACK_BOT_TOKEN, SLACK_APP_TOKEN, and optionally id (app id).
BOLT_CONFIG = {
    "id": os.getenv("SLACK_APP_ID", ""),
    "SLACK_BOT_TOKEN": os.getenv("SLACK_BOT_TOKEN", ""),
    "SLACK_APP_TOKEN": os.getenv("SLACK_APP_TOKEN", ""),
}
