from pydantic import BaseModel, Field
from typing import Optional
import uuid

from digitalhq.commons.common_types import Message, MessageStore
from digitalhq.state.base import BaseState


class BaseSession(BaseModel):
    sid: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        type=str,
        description="The session ID",
    )
    owner: str = Field(
        ..., description="The owner name of the session"
    )
    topic: str = Field(..., description="The topic of the session")
    is_completed: bool = Field(
        default=False, description="The status of the session"
    )
    participants: list = Field(
        default_factory=list,
        description="The participants in the session",
    )
    summary: str = Field(
        default=None, description="The summary of the session"
    )
    content: list[Message] = Field(
        default_factory=list, description="The content of the session"
    )
    parent: dict = Field(
        default_factory=dict, description="The parent session"
    )
    childs: dict = Field(
        default_factory=dict, description="The child sessions"
    )

    def _add_participant(self, participant: str):
        self.participants.append(participant)

    def _link_session(self, child_session: "BaseSession"):
        """Link the session to the parent session, but only temporarily.
        Using SessionStore.link_session for long-term linking."""
        self.childs[child_session.sid] = child_session
        child_session.parent[self.sid] = self

    def add_message(self, message: Message):
        self.content.append(message)
        if message.to_who:
            for human_name in message.to_who:
                if human_name not in self.participants:
                    self.participants.append(human_name)

    def change_owner(self, new_owner: str, stay: bool = False):
        if stay:
            self.participants.append(self.owner)
        self.owner = new_owner

    def create_child(
        self, owner: str, topic: str, message: Message = None
    ):
        """Create a child session from this session."""
        session = BaseSession(
            owner=owner, topic=topic, content=[message]
        )
        self._link_session(session)
        return session.sid

    def add_child(self, session: "BaseSession"):
        self._link_session(session)

    def __str__(self) -> str:
        return f"Session: {self.sid} - Messages: {self.content}"