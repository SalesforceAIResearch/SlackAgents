from collections import defaultdict
from typing import Any, List, Dict
import json

from slackagents.agent.workflow_agent import WorkflowAgent, ExecutionGraph
from slackagents.agent.base import BaseSlackAgent
from slackagents.llms.base import BaseLLMConfig, BaseLLM
from slackagents.llms.openai import OpenAILLM

class SlackWorkflowAgent(WorkflowAgent, BaseSlackAgent):
    
    def __init__(
        self,
        name: str,
        desc: str,
        graph: ExecutionGraph,
        max_steps: int = 10,
        llm: BaseLLM = OpenAILLM(BaseLLMConfig(model="gpt-4o")),
        messages: List[Dict[str, str]] = None,
        *args,
        **kwargs
    ):
        super().__init__(
            name=name,
            desc=desc,
            graph=graph,
            max_steps=max_steps,
            llm=llm,
            messages=messages,
            *args,
            **kwargs
        )
        self.sessions: Dict[str, List[Dict[str, str]]] = defaultdict(list)
    
    def chat(self, content: str, channel_id: str) -> str:
        """chat with the user in a given channel"""
        if channel_id not in self.sessions:
            self.sessions[channel_id].extend(self.messages)
        self._update_system_prompt()
        self.sessions[channel_id].append({"role": "user", "content": content})
        self.messages = self.sessions[channel_id] # this line is necessary to make sure the messages are updated through each session
        message = self.execute()
        # TODO: handle case when message is still a tool call so that ask user to confirm continue or stop
        return message["content"]
    
    def reset(self, channel_id: str):
        """reset the session for a given channel. Clear the conversation history."""
        self.sessions[channel_id] = [{"role": "system", "content": self.system_prompt}]
        if self.messages is not None:
            self.sessions[channel_id].extend(self.messages)