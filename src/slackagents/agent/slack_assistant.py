from collections import defaultdict
from typing import List, Dict
import json
import re
from slack_sdk import WebClient

from slackagents.agent.executor import Executor
from slackagents.commons.default_prompts import SLACK_ASSISTANT_PROMPT, SLACK_COLLEAGUES_PROMPT
from slackagents.tools.slack_agent_tools import send_message_tool, wait_tool, get_thread_history_tool
from slackagents.llms.base import BaseLLM, BaseLLMConfig
from slackagents.llms.openai import OpenAILLM
from slackagents.tools.base import BaseTool
from slackagents.slack.utils import get_thread_history, format_thread_history_to_conversation, block_message, get_channel_user_ids_and_names

from .base import BaseSlackAgent

class SlackAssistant(Executor, BaseSlackAgent):
    def __init__(
        self,
        name: str,
        desc: str,
        tools: List[BaseTool] = None,
        system_prompt: str = SLACK_ASSISTANT_PROMPT,
        tool_choice: str = "required",
        max_steps: int = 10,
        llm: BaseLLM = OpenAILLM(BaseLLMConfig(model="gpt-4o")),
        messages: List[Dict[str, str]] = None,
        slack_bot_token: str = None,
        bot_id: str = None,
        colleagues: Dict[str, Dict[str, str]] = None,
        *args,
        **kwargs
    ):
        # adding slack tools to the tools list
        tools = tools or []
        tools.append(send_message_tool)
        tools.append(wait_tool)
        # add get_thread_history_tool so that the agent can get the thread history if need more context
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
        # session stores the in-cache conversation history for each slack channel
        # key hierarchy: channel_id -> thread_ts -> messages
        self.sessions: Dict[str, Dict[str, List[Dict[str, str]]]] = defaultdict(lambda: defaultdict(list))
        self.slack_bot_token = slack_bot_token
        self.colleagues = colleagues # user_id -> {"name": name, "description": description}
        self.bot_id = bot_id
        self.channel_users = {}
        # Separate the system prompt into two parts: base system prompt and colleagues prompt
        # When system prompt is complex, such as containing `{` or `}` characters, 
        # `.format()` method will fail. So we separate the system prompt into two parts.
        if self.colleagues:
            self.system_prompt = system_prompt + "\n" + SLACK_COLLEAGUES_PROMPT.format(colleagues=json.dumps(self.colleague_info))
        else:
            self.system_prompt = system_prompt
    
    @property
    def colleague_info(self) -> Dict[str, str]:
        """Get the name and description of all colleagues."""
        if not self.colleagues:
            return {}
        return {info["name"]: info["description"] for user_id, info in self.colleagues.items()}
    
    def add_colleague(self, user_id: str, name: str, description: str):
        """Add a colleague to the list of colleagues."""
        self.colleagues[user_id] = {"description": description, "name": name}
        
    def _get_colleague_id(self, name: str, channel_id: str = None) -> str:
        """Get the user id of a colleague given the name."""
        for user_id, info in self.colleagues.items():
            if info["name"] == name:
                return user_id
        # TODO: get the user id from the channel users
        if channel_id:
            self._get_channel_users(channel_id)
        for user_id, user_name in self.channel_users[channel_id].items():
            if user_name == name:
                return user_id
        raise ValueError(f"User {name} not known")
    
    def _get_channel_users(self, channel_id: str) -> Dict[str, str]:
        """Get the user id and name of all users in a channel."""
        self.channel_users[channel_id] = get_channel_user_ids_and_names(channel_id, self.slack_bot_token)
        
    def _send_message(
        self, 
        channel_id: str, 
        thread_ts: str, 
        text: str, 
        to_whom: str = None
    ):
        """Send a message to a slack channel.
        
        Args:
            channel_id (str): the slack channel id
            thread_ts (str): the thread timestamp
            text (str): the message text
            to_who (str): the user name to mention, Default is None
        """
        client = WebClient(token=self.slack_bot_token)
        # get the user id based on the name
        mention_id = self._get_colleague_id(to_whom, channel_id)
        # add a space between the mention and the text (default for slack)
        text = f"<@{mention_id}>" + " " + text if mention_id else text
        # Convert to slack markdown
        client.chat_postMessage(
            channel=channel_id,
            blocks=[block_message(text)],
            thread_ts=thread_ts
        )
    
    def chat(
        self,
        content: str,
        channel_id: str,
        thread_ts: str,
        from_who: str,
        *args,
        **kwargs
    ) -> str:
        """chat with the user in a given slack channel under a thread.
        Agent will decide to call tool or respond. 
        TODO: chat as an event listener
        
        Args:
            content (str): the message content
            channel_id (str): the slack channel id
            thread_ts (str): the thread timestamp
            *args: additional arguments
            **kwargs: additional keyword arguments
        Returns:
            str: WebClientnse from the agent
        """
        if thread_ts not in self.sessions[channel_id]:
            self.sessions[channel_id][thread_ts].append({"role": "system", "content": self.system_prompt})
        self.sessions[channel_id][thread_ts].append({"role": "user", "content": content})
        self.messages = self.sessions[channel_id][thread_ts]
        self.execute(channel_id=channel_id, thread_ts=thread_ts)
        # TODO: return the last message or return a confirmation message to the user
    
    def _convert_mentions_to_name(self, message: str) -> str:
        """Convert mentions to names in the message."""
        # find all mentions in the message
        mentions = re.findall(r"<@(\w+)>", message)
        for mention in mentions:
            name = self._get_colleague_id(mention)
            message = message.replace(f"<@{mention}>", f"Mentioned {name}")
        return message
    
    def execute(
        self, 
        channel_id: str, 
        thread_ts: str, 
        *args, 
        **kwargs
    ):
        """execute the messages until no tool calls"""
        message = self.step()
        step_count = 0
        while message.get("tool_calls"):
            for tool_call_request in message["tool_calls"]:
                # TODO: handle case when tool call is not successful so that ask user to confirm continue or regenerate
                if tool_call_request["function"]["name"] == "send_message":
                    self.messages.append(message)
                    arguments = json.loads(tool_call_request["function"]["arguments"])
                    self._send_message(
                        channel_id=channel_id,
                        thread_ts=thread_ts,
                        text=arguments["content"],
                        to_whom=arguments["to_whom"]
                    )
                    tool_call_id = tool_call_request["id"]
                    tool_response = {"role": "tool", "content": f"Message sent to {arguments['to_whom']}. Waiting for response...", "tool_call_id": tool_call_id}
                    self.messages.append(tool_response)
                elif tool_call_request["function"]["name"] == "get_thread_history":
                    self.messages.append(message)
                elif tool_call_request["function"]["name"] == "wait":
                    continue
                
                else:
                    self.messages.append(message)
                    tool_response = self._process_tool_call(tool_call_request)
                    self.messages.append(tool_response)
            message = self.step()
            step_count += 1
            if step_count > self.max_steps:
                break
        return message