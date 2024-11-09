from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict, Union
from slackagents.commons.default_prompts import BASE_ASSISTANT_PROMPT
import os
import yaml
import warnings

class SlackConfig(BaseModel):
    id: str
    SLACK_BOT_TOKEN: str
    SLACK_APP_TOKEN: str

class LLMConfig(BaseModel):
    model: Optional[str] = "gpt-4o"
    temperature: float = 0.2
    max_tokens: int = 3000
    top_p: float = 0
    top_k: int = 1
    
class Colleague(BaseModel):
    name: str
    description: str
    
class ToolConfig(BaseModel):
    name: str
    type: Literal["function", "model", "llamaindex", "langchain", "crewai", "composio_openai"]
    module: str
    
class AssistantAgentConfig(BaseModel):
    name: str
    desc: str
    type: Literal["SlackAssistant", "SlackDMAssistant", "SlackChannelAssistant"] = "SlackAssistant"
    llm: Optional[LLMConfig] = None
    colleagues: Dict[str, Colleague] = {}
    tools: List[ToolConfig] = []    
    tool_choice: Literal["auto", "required"]
    max_steps: int = 10
    system_prompt: str
    verbose: bool = False

class TransitionConfig(BaseModel):
    source: str
    target: str
    description: str

class GraphConfig(BaseModel):
    nodes: dict[str, AssistantAgentConfig]
    transitions: List[TransitionConfig]
    initial_module: str

class WorkflowAgentConfig(BaseModel):
    name: str
    desc: str
    # TODO: add channel workflow runner, combination. currently only support dm workflow
    type: Literal["SlackWorkflow"]
    graph: GraphConfig
    max_steps: int = 10
    verbose: bool = False
    
    
class SlackAssistantConfig(BaseModel):
    slackConfig: SlackConfig
    agentConfig: AssistantAgentConfig

    @classmethod
    def from_yaml(cls, yaml_path: str) -> 'SlackAssistantConfig':
        if not os.path.exists(yaml_path):
            raise FileNotFoundError(f"The file {yaml_path} does not exist.")
        else:   
            with open(yaml_path, 'r') as file:
                config_dict = yaml.safe_load(file)
            if "system_prompt" in config_dict["agentConfig"]:
                # directly use the system prompt string in the config yaml file
                pass
            elif config_dict["agentConfig"]["system_prompt_file"] and os.path.exists(config_dict["agentConfig"]["system_prompt_file"]):
                with open(config_dict["agentConfig"]["system_prompt_file"], 'r') as file:
                    config_dict["agentConfig"]["system_prompt"] = file.read()
            else:
                warnings.warn("No system prompt provided, using default system prompt.")
                config_dict["agentConfig"]["system_prompt"] = BASE_ASSISTANT_PROMPT
            return cls.parse_obj(config_dict)

class SlackWorkflowConfig(BaseModel):
    slackConfig: SlackConfig
    agentConfig: WorkflowAgentConfig
    
    @classmethod
    def from_yaml(cls, yaml_path: str) -> 'SlackWorkflowConfig':
        if not os.path.exists(yaml_path):
            raise FileNotFoundError(f"The file {yaml_path} does not exist.")
        else:
            with open(yaml_path, 'r') as file:
                config_dict = yaml.safe_load(file)
            graph = config_dict["agentConfig"]["graph"]
            for node_id, node_config in graph["nodes"].items():
                if "system_prompt" in node_config:
                    # directly use the system prompt string in the config yaml file
                    pass
                elif node_config["system_prompt_file"] and os.path.exists(node_config["system_prompt_file"]):
                    with open(node_config["system_prompt_file"], 'r') as file:
                        node_config["system_prompt"] = file.read()
                else:
                    warnings.warn(f"No system prompt provided for node {node_id} in the workflow graph, using default system prompt.")
                    node_config["system_prompt"] = BASE_ASSISTANT_PROMPT
            return cls.parse_obj(config_dict)
        

class SlackAgentConfig(BaseModel):
    slackConfig: SlackConfig
    agentConfig: AssistantAgentConfig | WorkflowAgentConfig

    @classmethod
    def from_yaml(cls, yaml_path: str) -> Union[SlackAssistantConfig, SlackWorkflowConfig]:
        if not os.path.exists(yaml_path):
            raise FileNotFoundError(f"The file {yaml_path} does not exist.")
        else:
            with open(yaml_path, 'r') as file:
                config_dict = yaml.safe_load(file)
        # Parse the config object by whether it is a SlackAssistant or SlackWorkflow
        if isinstance(config_dict["agentConfig"], dict) and "type" in config_dict["agentConfig"]:
            if config_dict["agentConfig"]["type"] in ["SlackAssistant", "SlackDMAssistant", "SlackChannelAssistant"]:
                return SlackAssistantConfig.from_yaml(yaml_path)
            # TODO: add channel workflow runner, combination. currently only support dm workflow
            elif config_dict["agentConfig"]["type"] in ["SlackWorkflow"]:
                return SlackWorkflowConfig.from_yaml(yaml_path)
        else:
            raise ValueError(f"Invalid agent type: {config_dict['agentConfig']['type']}. The type must be either SlackAssistant, SlackDMAssistant, SlackChannelAssistant, SlackWorkflow")