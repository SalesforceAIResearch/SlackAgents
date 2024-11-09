from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from slackagents.agent.slack_assistant import SlackAssistant
from slackagents.agent.slack_dm_agent import SlackDMAgent
from slackagents.slack.utils import get_channel_user_ids_and_names, block_message

class SlackAppAgentRunner:
    def __init__(
        self,
        config: dict,
        dm_agent_config: dict,
        channel_agent_config: dict
    ):
        self.config = config
        self.dm_agent = SlackDMAgent(**dm_agent_config)
        self.channel_agent = SlackAssistant(**channel_agent_config)
        self.app = App(token=config.get("SLACK_BOT_TOKEN"))
        self.channel_user_id_name_map = {}
        self.bot_id = config.get("id")
        self._register_mention_handlers()
        self._register_dm_handlers()
        
    def _register_dm_handlers(self):
        @self.app.event("message")
        def handle_message(event, say, client):
            if event.get("channel_type") == "im":
                loading_message = say(f"🔮 *{self.dm_agent.name}* is brewin' some magic...✨")
                user_message = event["text"]
                # get the channel id
                channel_id = event["channel"]
                response = self.dm_agent.chat(user_message, channel_id)
                # Update the loading message with the response
                # Convert to slack markdown
                client.chat_update(
                    channel=channel_id,
                    ts = loading_message["ts"],
                    blocks=[block_message(response)]
                )
            else:
                # TODO: handle channel messages
                pass
   
    # Event listener for mention messages
    def _register_mention_handlers(self):
        @self.app.event("app_mention")
        def handle_message(event, say):
            # get the channel id
            channel_id = event["channel"]
            timestamp = event["ts"]
            thread_ts = event.get("thread_ts", timestamp)
            user_id = event["user"]
            # construct the message and replace mentions with names
            if user_id not in self.channel_user_id_name_map:
                channel_user_ids_and_names = get_channel_user_ids_and_names(channel_id, self.config.get("SLACK_BOT_TOKEN"))
                self.channel_user_id_name_map[user_id] = channel_user_ids_and_names[user_id]
            message = f"Message from {self.channel_user_id_name_map[user_id]}: "
            # TODO: handle multiple elements in the message
            # construct the message by converting the mention id to name
            for ele in event["blocks"][0]["elements"][0]["elements"]:
                if ele["type"] == "user":
                    mentioned_user_id = ele["user_id"]
                    # mentioned_user_id is not in the existing self.channel_user_id_name_map
                    if mentioned_user_id not in self.channel_user_id_name_map:
                        channel_user_ids_and_names = get_channel_user_ids_and_names(channel_id, self.config.get("SLACK_BOT_TOKEN"))
                        self.channel_user_id_name_map[mentioned_user_id] = channel_user_ids_and_names[mentioned_user_id]
                    if mentioned_user_id == self.bot_id:
                        message += "<mentioned you> "
                    else:
                        message += f"<mentioned {self.channel_user_id_name_map[mentioned_user_id]}> "
                elif ele["type"] == "text":
                    message += ele["text"]
                else:
                    # TODO: handle other types of elements
                    pass
            self.channel_agent.chat(message, channel_id, thread_ts, from_who=user_id)
            
    def run(self):
        SocketModeHandler(
            self.app, self.config.get("SLACK_APP_TOKEN")
        ).start()
   
