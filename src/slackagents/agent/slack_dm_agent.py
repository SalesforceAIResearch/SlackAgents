from collections import defaultdict
from typing import Any, List, Dict
import json

from slackagents.agent.assistant import Assistant
from slackagents.agent.base import BaseSlackAgent
from slackagents.agent.executor import Executor
from slackagents.llms.base import BaseLLMConfig, BaseLLM
from slackagents.llms.openai import OpenAILLM
from slackagents.tools.base import BaseTool, ToolCall
from slackagents.commons.default_prompts import BASE_ASSISTANT_PROMPT

class SlackDMAgent(Executor, BaseSlackAgent):
    
    def __init__(
        self,
        name: str,
        desc: str,
        tools: List[BaseTool] = None,
        system_prompt: str = BASE_ASSISTANT_PROMPT,
        tool_choice: str = "auto",
        max_steps: int = 10,
        llm: BaseLLM = OpenAILLM(BaseLLMConfig(model="gpt-4o")),
        messages: List[Dict[str, str]] = None,
        *args,
        **kwargs
    ):
        super().__init__(
            name=name,
            desc=desc,
            tools=tools,
            system_prompt=system_prompt,
            tool_choice=tool_choice,
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
