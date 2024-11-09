import uuid
import time

from typing import Dict, Optional, Tuple, Any, TypeAlias
from pydantic import BaseModel, Field


class MindState(BaseModel):
    """Data model for state."""

    state: str
    thoughts: Optional[str] = Field(
        default="", description="the name of the transition"
    )
    task: Optional[str] = Field(
        default="", description="the task you should do in this state"
    )


class MindTransition(BaseModel):
    """Data model for state transition."""

    source_state: MindState = Field(
        ..., description="source state of a transition"
    )
    target_state: MindState = Field(
        ..., description="target state of a transition"
    )
    tranistion_name: Optional[str] = Field(
        default="Unknow", description="the name of the transition"
    )


class Task(BaseModel):
    """Data model for task. Formatting the task request. Each task is the minimum unit of work."""

    task_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        type=str,
        description="The task ID",
    )
    created_time: float = Field(
        default_factory=lambda: time.time(),
        type=float,
        description="The time the task is created",
    )
    task_input: str = Field(
        ..., type=str, description="The input for the task"
    )
    parent_tasks: Optional[Dict[str, "Task"]] = Field(
        default_factory=dict, description="The parent tasks"
    )
    child_tasks: Optional[Dict[str, "Task"]] = Field(
        default_factory=dict, description="The child tasks"
    )

    def link_task(self, task: "Task"):
        """Link the task to the parent task"""
        self.child_tasks[task.task_id] = task
        task.parent_tasks[self.task_id] = self


class Trigger(BaseModel):
    """Data model for trigger. Formatting the trigger request."""

    trigger_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        type=str,
        description="The trigger ID",
    )
    trigger_type: str = Field(
        ..., type=str, description="The type of the trigger"
    )
    trigger_info: str = Field(
        ..., type=str, description="The input for the trigger"
    )

    @property
    def info(self):
        return f"{self.trigger_type}: {self.trigger_info}"


class Message(BaseModel):
    """Data model for message. Formatting the message request."""

    mid: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        type=str,
        description="The message ID",
    )
    # time: float = Field(
    #     default_factory=lambda: time.time(),
    #     type=float,
    #     description="The time the message is created",
    # )
    type: str = Field(..., description="The type of the message")
    info: Any = Field(..., description="The input for the message")
    from_who: str = Field(
        ..., type=str, description="The sender of the message"
    )
    to_who: Optional[list[str]] = Field(
        default_factory=list,
        description="The receiver of the message",
    )

    # def __str__(self):
    #     return (
    #         f"{self.from_who}<Type: {self.type} Info: {self.info}> to"
    #         f" {self.to_who}"
    #     )


class SlackSessionID(BaseModel):
    channel_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="The slack channel ID",
    )
    thread_ts: Optional[str] = Field(
        default_factory=lambda: str(time.time()),
        description="The slack thread timestamp",
    )

    def __repr__(self) -> str:
        return f"{self.channel_id}/{self.thread_ts}"

    def __str__(self) -> str:
        return f"{self.channel_id}/{self.thread_ts}"

    def __eq__(self, other):
        if isinstance(other, SlackSessionID):
            return other == self.__str__()
        return False

    def __hash__(self):
        return hash(self.__str__())


MessageStore: TypeAlias = dict[str, list[Message]]
