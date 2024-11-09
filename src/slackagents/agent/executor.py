from abc import ABC, abstractmethod
from typing import Any, List, Dict
import json
import logging
from termcolor import colored

from slackagents.agent.base import BaseExecutor
from slackagents.llms.base import BaseLLMConfig, BaseLLM
from slackagents.llms.openai import OpenAILLM
from slackagents.tools.base import BaseTool, ToolCall
from slackagents.commons.default_prompts import BASE_ASSISTANT_PROMPT


class Executor(BaseExecutor):
    """
    Executor is a worker that executes a list of tools.
    """
    def __init__(self,
        name: str,
        desc: str, 
        tools: List[BaseTool] = None,
        system_prompt: str = BASE_ASSISTANT_PROMPT,
        tool_choice: str = "auto",
        max_steps: int = 10,
        llm: BaseLLM = OpenAILLM(BaseLLMConfig(model="gpt-4o")),
        messages: List[Dict[str, str]] = None,
        verbose: bool = False,
        *args: Any, 
        **kwargs: Any
    ):
        super().__init__(name, desc)
        self.llm = llm
        if tools is None:
            tools = []
        self.tools = tools
        self.tool_name_to_tool = {tool.info["function"]["name"]: tool for tool in tools}
        self.system_prompt = system_prompt
        self.messages = [] if messages is None else messages
        self.messages.append({"role": "system", "content": self.system_prompt})
        self.tool_choice = tool_choice
        self.max_steps = max_steps
        self.verbose = verbose
    
    def step(self) -> Dict[str, str]:
        """step to llm to generate a response message"""
        tool_info = [tool.info for tool in self.tools]
        if self.verbose:
            self._log_messages()

        response = self.llm.chat_completion(
            self.messages,
            tools=tool_info,
            tool_choice=self.tool_choice
        )
        message = {"role": "assistant", **response}
        return message
    
    def add_message(self, message: Dict[str, str]):
        self.messages.append(message)
    
    def __call__(self, *args, **kwargs):
        return self.execute(*args, **kwargs)
    
    def execute(self, *args, **kwargs):
        """execute the messages until no tool calls"""
        message = self.step()
        self.messages.append(message)
        step_count = 0
        while message.get("tool_calls"):
            for tool_call_request in message["tool_calls"]:
                # TODO: handle case when tool call is not successful so that ask user to confirm continue or regenerate
                # TODO: using only the first tool call even if there are multiple and keep generating until no tool calls
                tool_response = self._process_tool_call(tool_call_request)
                self.messages.append(tool_response)
            message = self.step()
            self.messages.append(message)
            step_count += 1
            if step_count > self.max_steps:
                break
        return message

    def _process_tool_call(self, tool_call_request: Dict[str, Any]) -> Dict[str, Any]:
        if self.verbose:
            self._log_tool_call_request(tool_call_request)

        name = tool_call_request["function"]["name"]
        arguments = json.loads(tool_call_request["function"]["arguments"])
        tool = self.get_tool(name)
        id = tool_call_request["id"]
        
        processed_tool_call = ToolCall(name=name, arguments=arguments, id=id)
        output = tool.execute(processed_tool_call)
        
        tool_response = {"role": "tool", "content": output, "tool_call_id": id}

        if self.verbose:
            self._log_tool_call_output(tool_response)

        return tool_response
    
    def get_tool(self, tool_name: str) -> BaseTool:
        return self.tool_name_to_tool[tool_name]
    
    def add_tool(self, tool: BaseTool):
        self.tools.append(tool)
        self.tool_name_to_tool[tool.info["function"]["name"]] = tool
    
    def _log_tool_call_request(self, tool_call_request: Dict[str, Any]):
        formatted_request = json.dumps(tool_call_request, indent=2)
        colored_request = colored(formatted_request, "cyan")
        print("\nTool Call Request:")
        print(colored_request)

    def _log_tool_call_output(self, tool_response: Dict[str, Any]):
        formatted_output = json.dumps(tool_response, indent=2)
        colored_output = colored(formatted_output, "green")
        print("\nTool Call Output:")
        print(colored_output)

    def _log_messages(self):
        formatted_messages = json.dumps(self.messages, indent=2)
        colored_messages = colored(formatted_messages, "light_blue")
        print("\nMessages:")
        print(colored_messages)


    
        
        