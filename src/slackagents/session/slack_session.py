from pydantic import Field
import time

from slack_sdk import WebClient
from digitalhq.commons.common_types import Message, SlackSessionID

from digitalhq.session.base import BaseSession

# TODO: Add the slack user id map into world_client as API
id_map = {
    "Weiran Yao": "U06V9R7FCLB", 
    "chatwoot": "A015GST9RJ6",
    "Kate": "U071KCG20KC", 
    "Jane": "U0704DKTLE6",
    "zhiwei": "U0706S5BYE8", 
    "caiming xiong": "U070SCDGAKD",
    "John": "U071Y175CTT",
    "Sam": "U0728DDNGQY",
    "caiming": "A015GST9RJ6"
}

class SlackSession(BaseSession):
    channel_id: str = Field(
        default="C06V9R88Y9Z", description="The slack channel ID"
    )
    thread_ts: str = Field(
        default=f"{time.time():.6f}", description="The slack thread timestamp"
    )
    
    def post(self, slack_bot_token: str, with_mention: bool = False):
        """Post most recent message to slack."""
        message = self.content[-1]
        self.post_message(message, slack_bot_token, with_mention=with_mention)
    
    def post_message(
        self,   
        message: Message,
        slack_bot_token: str,
        thread_ts: str = None,
        with_mention: bool = False,
    ):
        """Post a message to a slack channel."""
        """TODO: send the message to slack."""
        client = WebClient(token=slack_bot_token)
        if "caiming" in message.to_who:
            message.to_who.remove("caiming")  # no need to mention chatwoot
        if with_mention and message.to_who:
            slack_text = self._mention_format(str(message.info), message.to_who)
        else:
            slack_text = str(message.info)
        slack_response = client.chat_postMessage(
            text=slack_text,
            channel=self.channel_id,
            thread_ts=thread_ts,
        )
        return slack_response

    def get_parent_sid(self):
        return self.parent.keys()
    
    def get_child_sid(self):
        return self.childs.keys()
    
    def get_parent(self, session_store):
        parent_sid = self.get_parent_sid()
        parent = {}
        if parent_sid:
            parent = {parent_sid: session_store.get(parent_sid)}
        return parent
        
    def get_childs(self, session_store):
        child_sids = self.get_child_sid()
        childs = {}
        if child_sids:
            for child_sid in child_sids:
                childs[child_sid] = session_store.get(child_sid)
        return childs
    
    def create_child(
        self, session_store, owner: str, topic: str, channel_id: str, message: Message = None
    ):
        """Create a child session from this session."""
        Warning("Deprecated. Use SessionStore.link_session instead.")
        thread_ts = f"{time.time():.6f}"
        child_session_id = SlackSessionID(channel_id=channel_id, thread_ts=thread_ts)
        sid = str(child_session_id)
        session = SlackSession(
            sid=sid, owner=owner, topic=topic, content=[message], channel_id=channel_id
        )
        self._link_session(session)
        session_store.add(session)
        session_store.add(self)
                
        return session
    
    def _mention_format(self, text:str, to_who:list[str]) -> str:
        mention_str = " ".join([f"<@{id_map[user_name]}>" for user_name in to_who if user_name in id_map])
        return f"{mention_str} {text}"