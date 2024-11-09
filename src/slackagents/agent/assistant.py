from typing import Any, List, Dict
import json

from slackagents.agent.base import BaseAssistant
from slackagents.agent.executor import Executor
from slackagents.llms.base import BaseLLMConfig, BaseLLM
from slackagents.llms.openai import OpenAILLM
from slackagents.tools.base import BaseTool, ToolCall
from slackagents.commons.default_prompts import BASE_ASSISTANT_PROMPT

class Assistant(Executor, BaseAssistant):
    """Exposing the chat method to the user from the tool executor"""
    
    def chat(self, content: str) -> str:
        self.messages.append({"role": "user", "content": content})
        message = self.execute()
        # TODO: handle case when message is still a tool call so that ask user to confirm continue or stop
        return message["content"]