from typing import Dict, List, Union
import importlib
import os
from slackagents import (
    Assistant, 
    SlackAssistant,
    SlackWorkflowAgent,
    SlackDMAgent,
    BaseLLMConfig, 
    OpenAILLM
)
from slackagents.tools.base import BaseTool
from slackagents.slack.handler import (
    SlackDMHandler, 
    SlackChannelHandler
)
from slackagents.graph.execution_graph import (
    ExecutionGraph, 
    ExecutionTransition
)
from slackagents.slack.slack_agent_runner import SlackAppAgentRunner

from slackagents.commons.configuration_schemas import (
    SlackAgentConfig, 
    SlackAssistantConfig, 
    SlackWorkflowConfig, 
    AssistantAgentConfig
)

class AutoSlackAgent:
    """
    A class to create Slack agents from configurations.    
    """
    def __init__(self):
        raise EnvironmentError(
            "AutoSlackAgent is designed to be instantiated "
            "using the `AutoSlackAgent.from_config(config)` "
            "or `AutoSlackAgent.from_yaml(yaml_path)` methods."
        )

    @classmethod
    def from_config(cls, config: Union[SlackAgentConfig, SlackAssistantConfig, SlackWorkflowConfig, Dict, str]) -> Union[SlackAppAgentRunner, SlackDMHandler, SlackChannelHandler]:
        """
        Create a Slack agent from a standard configuration.
        
        :param config: a standard SlackAgentConfig object defined in configuration_schemas.py, a dictionary for the config that matches the SlackAgentConfig schema, or a YAML file path to a config file that matches the SlackAgentConfig schema
        :type config: Union[SlackAgentConfig, SlackAssistantConfig, SlackWorkflowConfig, Dict, str]
        :return: a SlackAppAgentRunner, SlackDMHandler, or SlackChannelHandler object
        :rtype: Union[SlackAppAgentRunner, SlackDMHandler, SlackChannelHandler]
        """
        if isinstance(config, str):
            if config.endswith('.yaml') or config.endswith('.yml'):
                if os.path.exists(config):
                    config = SlackAgentConfig.from_yaml(config)
                else:
                    raise FileNotFoundError(f"The file {config} does not exist.")
            else:
                raise ValueError(f"The file {config} is not a valid YAML file.")
        elif isinstance(config, dict):
            config = SlackAgentConfig(**config)
        elif isinstance(config, SlackAgentConfig):
            pass
        else:
            raise ValueError(f"The input {config} is not a valid configuration.")
        if config.agentConfig.type in ["SlackAssistant", "SlackDMAssistant", "SlackChannelAssistant"]:
            return cls._create_assistant(config)
        # TODO: add channel workflow runner, combination. currently only support dm workflow
        elif config.agentConfig.type in ["SlackWorkflow"]:
            return cls._create_workflow(config)
        else:
            raise ValueError(f"The agent type {config.agentConfig.type} is not supported. Supported types are: SlackAssistant, SlackDMAssistant, SlackChannelAssistant, SlackWorkflow, SlackDMWorkflow, SlackChannelWorkflow.")
    
    @classmethod
    def from_yaml(cls, yaml_path: str) -> Union[SlackAppAgentRunner, SlackDMHandler, SlackChannelHandler]:
        """
        Create a Slack agent from a YAML file.
        
        :param yaml_path: the path to a YAML file that matches the SlackAssistantConfig schema
        :type yaml_path: str
        :return: a SlackAppAgentRunner, SlackDMHandler, or SlackChannelHandler object
        :rtype: Union[SlackAppAgentRunner, SlackDMHandler, SlackChannelHandler]
        """
        if isinstance(yaml_path, str):
            if yaml_path.endswith('.yaml') or yaml_path.endswith('.yml'):
                if os.path.exists(yaml_path):   
                    config = SlackAgentConfig.from_yaml(yaml_path)
                else:
                    raise FileNotFoundError(f"The file {yaml_path} does not exist.")
            else:
                raise ValueError(f"The file {yaml_path} is not a valid YAML file.")
        if config.agentConfig.type in ["SlackAssistant", "SlackDMAssistant", "SlackChannelAssistant"]:
            return cls._create_assistant(config)
        # TODO: add channel workflow runner, combination. currently only support dm workflow
        elif config.agentConfig.type in ["SlackWorkflow"]:
            return cls._create_workflow(config)
        else:
            raise ValueError(f"The agent type {config.agentConfig.type} is not supported. Supported types are: SlackAssistant, SlackDMAssistant, SlackChannelAssistant, SlackWorkflow, SlackDMWorkflow, SlackChannelWorkflow.")
    
    @classmethod
    def _create_llm(cls, config: AssistantAgentConfig) -> OpenAILLM:
        if config.llm:
            llm_config = BaseLLMConfig(**config.llm.dict())
        else:
            llm_config = BaseLLMConfig()
        
        return OpenAILLM(llm_config)

    @classmethod
    def _create_tools(cls, config: AssistantAgentConfig) -> List[BaseTool]:
        tools = []
        for tool_config in config.tools if config.tools else []:
            name = tool_config.name
            module_path = tool_config.module
            try:
                module = importlib.import_module(module_path)
            except ModuleNotFoundError:
                raise ModuleNotFoundError(f"The module {module_path} does not exist.")
            tool = getattr(module, name)
            tools.append(tool)
        return tools

    @classmethod
    def _create_assistant(cls, config: SlackAssistantConfig) -> Union[SlackAppAgentRunner, SlackDMHandler, SlackChannelHandler]:
        # Create tools and llm instance with the config
        assert isinstance(config, SlackAssistantConfig), "The config must be a SlackAssistantConfig object."
        tools = cls._create_tools(config.agentConfig)
        llm = cls._create_llm(config.agentConfig)
        slack_config = config.slackConfig.dict()
        if config.agentConfig.type == "SlackAssistant":
            # dm handler config
            dm_agent_config = config.agentConfig.dict()
            # Prevent referencing the same tools object for both dm and channel agents
            dm_agent_config["tools"] = tools + [] 
            dm_agent_config["llm"] = llm
            # set tool choice to auto
            dm_agent_config["tool_choice"] = "auto"
            # remove colleagues from the config
            dm_agent_config.pop("colleagues")
            # channel handler config
            channel_agent_config = config.agentConfig.dict()
            # Prevent referencing the same tools object for both dm and channel agents
            channel_agent_config["tools"] = tools + []
            channel_agent_config["llm"] = llm
            # set tool choice to required
            channel_agent_config["tool_choice"] = "required"
            # add slack tokens to channel agent config
            channel_agent_config["slack_bot_token"] = slack_config["SLACK_BOT_TOKEN"]
            channel_agent_config["bot_id"] = slack_config["id"]
            runner = SlackAppAgentRunner(slack_config, dm_agent_config, channel_agent_config)
            return runner
        elif config.agentConfig.type == "SlackDMAssistant":
            agent_config = config.agentConfig.dict()
            agent_config["tools"] = tools
            agent_config["llm"] = llm
            agent = SlackDMAgent(**agent_config)
            runner = SlackDMHandler(slack_config, agent)
            return runner
        elif config.agentConfig.type == "SlackChannelAssistant":
            agent_config = config.agentConfig.dict()
            agent_config["tools"] = tools
            agent_config["llm"] = llm
            # set tool choice to required for channel assistant
            agent_config["tool_choice"] = "required"
            agent = SlackAssistant(**agent_config)
            runner = SlackChannelHandler(slack_config, agent)
            return runner
        else:
            raise ValueError(f"The agent type {config.agentConfig.type} is not supported. Supported types are: SlackAssistant, SlackDMAssistant, SlackChannelAssistant.")
    
    @classmethod
    def _create_workflow(cls, config: SlackWorkflowConfig) -> Union[SlackAppAgentRunner, SlackDMHandler, SlackChannelHandler]:
        assert isinstance(config, SlackWorkflowConfig), "The config must be a SlackWorkflowConfig object."
        slack_config = config.slackConfig.dict()
        agent_config = config.agentConfig.dict()
        graph_config = agent_config["graph"]
        graph = ExecutionGraph()
        for node_id, node_config in graph_config["nodes"].items():
            tools = cls._create_tools(AssistantAgentConfig(**node_config))
            llm = cls._create_llm(AssistantAgentConfig(**node_config))
            node_config["tools"] = tools
            node_config["llm"] = llm
            agent = Assistant(**node_config)
            graph.add_agent(agent)
        for transition in graph_config["transitions"]:
            graph.add_transition(
                ExecutionTransition(
                    source_module=graph.get_module(transition["source"]),
                    target_module=graph.get_module(transition["target"]),
                    desc=transition["description"]
                )
            )
        graph.set_initial_module(graph.get_module(graph_config["initial_module"]))
        agent = SlackWorkflowAgent(
            name=agent_config["name"],
            desc=agent_config["desc"],
            graph=graph,
            llm=llm,
            max_steps=agent_config["max_steps"],
            verbose=agent_config["verbose"]
        )
        if config.agentConfig.type == "SlackWorkflow":
            runner = SlackDMHandler(slack_config, agent)
            return runner
        # TODO: add channel workflow runner, combination. currently only support dm workflow
        else:
            raise ValueError(f"The agent type {config.agentConfig.type} is not supported. Supported types are: SlackWorkflow.")