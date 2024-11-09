from pydantic import BaseModel, Field
from digitalhq.commons.common_types import Message, SlackSessionID
from digitalhq.session.base import BaseSession
from digitalhq.session.slack_session import SlackSession
import pickle
import redis
from redis import Redis
from typing import Any, Optional

# TODO: Add redis url to the environment variables
REDIS_URL = "redis://localhost:6379/"


class SessionStore(BaseModel):
    """Human sessions."""

    sessions: dict[str, BaseSession] = Field(
        default_factory=dict, description="The sessions for the human"
    )
    
    def add(self, session: BaseSession):
        """Add a session to the session store."""
        self.sessions[session.sid] = session

    def get(self, session_id: str) -> BaseSession:
        """Get a session from a session store."""
        if self.if_exists(session_id):            
            return self.sessions[session_id]
        else:
            return None
    
    def if_exists(self, session_id: str) -> bool:
        """Check if a session exists in the session store."""
        return True if session_id in self.sessions else False

    def create_session(
        self, message: Message, **kwargs
    ) -> BaseSession:
        """Create a session with message object."""
        session = BaseSession(
            owner=message.from_who,
            topic=message.info, 
            content=[message]
        )
        self.add(session)
        return session

    def add_message(self, session_id: str, message: Message):
        """Add a message to the session."""
        session = self.get(session_id)
        if session:
            session.add_message(message)
        else:
            raise ValueError("Session not found")
        
    def complete_session(self, session_id: str, summary: str):
        """Complete a session."""
        session = self.get(session_id)
        if session:
            session.is_completed = True
            session.summary = summary
            self.add(session)
        else:
            raise ValueError("Session not found")
    
    def link_session(self, parent_sid: str, child_sid: str):
        """Link a child session to a parent session."""
        parent_session = self.get(parent_sid)
        child_session = self.get(child_sid)
        parent_session._link_session(child_session)
        self.add(parent_session)
        self.add(child_session)


class SlackSessionStore(SessionStore):
    channel_id: str = Field(
        default="C06V9R88Y9Z", description="The slack channel ID"
    )
    def get(self, session_id: str) -> SlackSession:
        """Get a session from a session store."""
        if self.if_exists(session_id):            
            return self.sessions[session_id]
        else:
            return None

    def create_session(
        self, message: Message, thread_ts:str, channle_id:str=None,  **kwargs
    ) -> SlackSession:
        """Create a session with message object from slack."""
        if channle_id:
            channel_id = channle_id
        else:
            channel_id = self.channel_id
        sid = str(SlackSessionID(
            channel_id=channel_id,
            thread_ts=thread_ts
        ))
        session = SlackSession(
            sid=sid,
            owner=message.from_who,
            topic=message.info,
            content=[message],
            channel=self.channel_id,
            thread_ts=thread_ts,
        )
        self.add(session)
        return session
    
    def new_session(self, message: Message, **kwargs):
        """Create a new session with message object from state run."""
        sid = SlackSessionID()
        session = SlackSession(
            sid=str(sid),
            owner=message.from_who,
            topic=message.info,
            content=[message],
            channel=sid.channel_id,
            thread_ts=sid.thread_ts,
        )
        return session
    
    def session_to_slack(self, session: SlackSession, channel_id: str, thread_ts: str):
        """link the session to slack thread."""
        session.channel_id = channel_id
        session.thread_ts = thread_ts
        session.sid = str(SlackSessionID(channel_id=channel_id, thread_ts=thread_ts))
        self.add(session)
        return session

class RedisSessionStore(SlackSessionStore):
    client: Any = Field(
        default_factory=lambda: redis.from_url(REDIS_URL),
        description="The redis client",
    )
    ttl: Optional[int] = Field(
        default=None, 
        description="The time to live for the session in seconds. Default is None for persist memory."
    )
    
    def add(self, session: SlackSession):
        """Add a session to the session store."""
        self.client.set(session.sid, pickle.dumps(session))
        if self.ttl:
            self.client.expire(session.sid, self.ttl)
            
    def get(self, session_id: str) -> SlackSession:
        """Get a session from a session store."""
        session = self.client.get(session_id)
        if session:
            return pickle.loads(session)
        else:
            return None

    def if_exists(self, session_id: str) -> bool:
        return self.client.exists(session_id)

    def create_session(
        self,
        message: Message,
        thread_ts: str,
        channle_id: str = None,
        **kwargs,
    ) -> SlackSession:
        session = super().create_session(
            message, thread_ts, channle_id, **kwargs
        )
        self.add(session)
        return session

    def add_message(self, session_id: str, message: Message):
        session = self.get(session_id)
        if session:
            session.add_message(message)
            self.add(session)
        else:
            raise ValueError("Session not found")
        


if __name__ == "__main__":
    session_store = RedisSessionStore()
    message = Message(type="task", info="chatting", from_who="jane")
    session = session_store.create_session(
        message=message,
        thread_ts="1714183719.136469",
        channle_id="C06V9R88Y9Z",
    )

    print(session)
    session = session_store.get(session.sid)
    print(session)
    
    print(session_store.if_exists(session.sid))
    session_store.add_message(session.sid, message)
    session = session_store.get(session.sid)
    print(session)
    
