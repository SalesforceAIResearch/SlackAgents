from slack_sdk import WebClient
import os
import json

# load the manifest
with open("example_manifest.json", "r") as f:
    manifest = json.load(f)
# loading agent config
with open("agent_config.json", "r") as f:
    agent_config = json.load(f)
# update the manifest to match the agent name
manifest["display_information"]["name"] = agent_config["name"]
manifest["features"]["bot_user"]["display_name"] = agent_config["name"]

# create the slack app with the manifest
token = os.getenv("SLACK_APP_CONFIG_TOKEN")
client = WebClient(token=token)

response = client.apps_manifest_create(manifest=manifest)
app_id = response["app_id"] # get the app id
bolt_config = {
    "id": app_id,
    "SLACK_BOT_TOKEN": "Update_me",
    "SLACK_APP_TOKEN": "Update_me"
}
# saving the id to a json file
with open("slack_bolt_id.json", "w") as f:
    json.dump(bolt_config, f, indent=4)