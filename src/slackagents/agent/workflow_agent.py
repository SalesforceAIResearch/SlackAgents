import json
from typing import Dict, List, Any
from termcolor import colored

from slackagents.agent.base import BaseAgent
from slackagents.llms.base import BaseLLM
from slackagents.llms.openai import OpenAILLM, BaseLLMConfig
from slackagents.graph.execution_graph import ExecutionGraph
from slackagents.commons.prompts.transition_function_prompt import TRANSITION_FUNCTION_TEMPLATE
from slackagents.commons.prompts.restart_function_prompt import RESTART_FUNCTION_TEMPLATE
class WorkflowAgent(BaseAgent):
    def __init__(
        self,
        name: str,
        desc: str,
        graph: ExecutionGraph,
        llm: BaseLLM = OpenAILLM(BaseLLMConfig(model="gpt-4")),
        messages: List[Dict[str, str]] = None,
        max_steps: int = 10,
        verbose: bool = False,
        *args: Any,
        **kwargs: Any
    ):
        super().__init__(name, desc)
        self.graph = graph
        self.cur_module = graph.initial_module
        self.llm = llm
        self.messages = [] if messages is None else messages
        self.max_steps = max_steps
        self.verbose = verbose
        # Synchronize verbose flag for all sub-modules in the graph
        for node in self.graph.nodes:
            module = self.graph.get_module(node)
            module.executor.verbose = verbose
    
    def chat(self, content: str):
        self._update_system_prompt()
        self.messages.append({"role": "user", "content": content})
        message = self.execute()
        return message["content"]

    def _update_system_prompt(self):
        system_prompt = self.cur_module.executor.system_prompt
        if len(self.messages) == 0:
            self.messages.append({"role": "system", "content": system_prompt})
        elif self.messages[0]["role"] == "system":
            self.messages[0]["content"] = system_prompt
        else:
            self.messages.insert(0, {"role": "system", "content": system_prompt})

    def step(self):
        transitions = self.graph.get_all_transitions(self.cur_module)
        doc_transitions_formatted = " ".join([f"{i+1}. `{t.target_module.name}`: {t.desc}" for i, t in enumerate(transitions)])
        transition_function = TRANSITION_FUNCTION_TEMPLATE.format(transitions=doc_transitions_formatted)
        restart_function = RESTART_FUNCTION_TEMPLATE
        transition_tool = [json.loads(transition_function)]
        restart_tool = [json.loads(restart_function)]
        cur_module_tools = [tool.info for tool in self.cur_module.executor.tools]
        tools = cur_module_tools + transition_tool + restart_tool
        if self.verbose:
            self._log_messages()

        response = self.llm.chat_completion(
            self.messages,
            tools=tools,
            tool_choice="auto"
        )
        return {"role": "assistant", **response}

    def _process_tool_call(self, tool_call_request: Dict[str, Any]):
        if tool_call_request["function"]["name"] == "transition":
            return self._handle_transition(tool_call_request)
        elif tool_call_request["function"]["name"] == "restart_workflow":
            return self._handle_restart(tool_call_request)
        else:
            return self.cur_module.executor._process_tool_call(tool_call_request)

    def _handle_transition(self, tool_call_request: Dict[str, Any]):
        arguments = json.loads(tool_call_request["function"]["arguments"])
        next_module_name = arguments["next_module"]
        reason = arguments["reason"]
        summary = arguments["summary"]
        self.cur_module = self.graph.get_module(next_module_name)
        
        transition_message = {
            "role": "tool",
            "content": f"You are now in the {self.cur_module.name} module. Reason: {reason}. Summary: {summary}. Tell the user about the workflow progress and what you are going to do next.",
            "tool_call_id": tool_call_request["id"]
        }
        if self.verbose:
            self._log_transition_message(transition_message)

        self.messages.append(transition_message)
        self._update_system_prompt()

    def _handle_restart(self, tool_call_request: Dict[str, Any]):
        arguments = json.loads(tool_call_request["function"]["arguments"])
        summary = arguments["summary"]
        reason = arguments["reason"]
        self.cur_module = self.graph.initial_module
        restart_message = {
            "role": "tool",
            "content": f"You have restarted the workflow. Summary: {summary}. Reason: {reason}.",
            "tool_call_id": tool_call_request["id"]
        }
        if self.verbose:
            self._log_restart_message(restart_message)
        self.messages.append(restart_message)
        self._update_system_prompt()

    def execute(self):
        step_count = 0
        while step_count < self.max_steps:
            message = self.step()
            self.messages.append(message)
            
            if not message.get("tool_calls"):
                break
            
            for tool_call in message["tool_calls"]:
                tool_response = self._process_tool_call(tool_call)
                if tool_response:
                    self.messages.append(tool_response)
            
            step_count += 1

        return message

    def _log_messages(self):
        formatted_messages = json.dumps(self.messages, indent=2)
        colored_messages = colored(formatted_messages, "light_blue")
        print("\nMessages:")
        print(colored_messages)
    
    def _log_transition_message(self, transition_message: Dict[str, Any]):
        formatted_transition_message = json.dumps(transition_message, indent=2)
        colored_transition_message = colored(formatted_transition_message, "light_yellow")
        print("\nTransition:")
        print(colored_transition_message)
    
    def _log_restart_message(self, restart_message: Dict[str, Any]):
        formatted_restart_message = json.dumps(restart_message, indent=2)
        colored_restart_message = colored(formatted_restart_message, "light_yellow")
        print("\nRestart Workflow:")
        print(colored_restart_message)