import os
from datetime import datetime
import click
import logging
from slackagents.commons.meta_schemas import generate_assistant, generate_workflow_agent
from slackagents.cli.config import load_config, save_config

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def create_agent(app_id, bot_token, app_token, name, description, type, root_folder):
    """Create a new Slack agent."""
    config = load_config()
    app_id, bot_token, app_token, name, description, root_folder = map(str.strip, [app_id, bot_token, app_token, name, description, root_folder])
    click.echo(click.style(f"Auto creating agent: {name}", fg="green"))
    processed_name_with_dashes = "-".join(name.lower().strip().split(" "))
    processed_name_with_underscores = "_".join(name.lower().strip().split(" "))
    # Create agent-specific folder within the project root
    agent_folder = os.path.join(root_folder, processed_name_with_dashes)
    # Check if the agent folder already exists
    if os.path.exists(agent_folder):
        click.echo(click.style(f"Agent folder already exists: {agent_folder}", fg="red"))
        return
    
    # Create the project folder if it doesn't exist
    click.echo(click.style(f"Creating agent folder: {agent_folder}", fg="yellow"))
    os.makedirs(agent_folder)
    os.makedirs(os.path.join(agent_folder, "prompts"))
    os.makedirs(os.path.join(agent_folder, "tools"))
    click.echo(click.style("Agent folder created successfully!", fg="green"))    
    # Generate the assistant
    if type in ["SlackAssistant", "SlackDMAssistant", "SlackChannelAssistant"]:
        click.echo(click.style("Generating system instructions and recommended tools...", fg="yellow"))
        assistant_schema = generate_assistant(f"Name: {name}. Description: {description}.")
        click.echo(click.style("System instructions and recommended tools generated successfully!", fg="green"))
        
        system_prompt = assistant_schema["system_prompt"]
        with open(os.path.join(agent_folder, f"prompts/{processed_name_with_underscores}.md"), "w") as f:
            f.write(system_prompt)
        # Create config.yaml
        config_yaml = f"""
slackConfig:
  id: {app_id}
  SLACK_BOT_TOKEN: {bot_token}
  SLACK_APP_TOKEN: {app_token}
agentConfig:
  name: {name}
  desc: {description}
  type: {type}
  system_prompt_file: prompts/{processed_name_with_underscores}.md
  llm:
    model: gpt-4o
    temperature: 0.2
  tools:
    - name: example_tool
      type: function
      module: tools
  tool_choice: auto
  max_steps: 10
  verbose: true
""".strip()
    elif type == "SlackWorkflow":
        click.echo(click.style("Generating workflow agent...", fg="yellow"))
        workflow_schema = generate_workflow_agent(f"Name: {name}. Description: {description}.")
        click.echo(click.style("Workflow agent generated successfully!", fg="green"))
        # Start building the nodes section dynamically
        nodes_yaml = ""
        for node_id, node in workflow_schema["nodes"].items():
            tools_yaml = ""
            for tool in node["tools"]:
                tools_yaml += f"""
          - name: {tool['name']}
            type: function
            module: tools"""

            nodes_yaml += f"""
      {node_id}:
        name: {node['name']}
        desc: {node['desc']}
        system_prompt_file: prompts/{node_id}.md
        llm:
          model: gpt-4o
          temperature: 0.2
        tools:{tools_yaml}
        tool_choice: auto
"""
            with open(os.path.join(agent_folder, f"prompts/{node_id}.md"), "w") as f:
                f.write(node["system_prompt"])
        # Build transitions section
        transitions_yaml = ""
        for transition in workflow_schema["transitions"]:
            transitions_yaml += f"""
      - source: {transition['source']}
        target: {transition['target']}
        description: {transition['description']}"""

        config_yaml = f"""
slackConfig:
  id: {app_id}
  SLACK_BOT_TOKEN: {bot_token}
  SLACK_APP_TOKEN: {app_token}

agentConfig:
  name: {name}
  desc: {description}
  type: {type}
  graph:
    nodes:{nodes_yaml}

    transitions:{transitions_yaml}
        
    initial_module: {workflow_schema["initial_module"]}
  max_steps: 10
  verbose: true
""".strip()

    # Write the config.yaml file for both types
    with open(os.path.join(agent_folder, "config.yaml"), "w") as f:
        f.write(config_yaml)
    # Create requirements.txt
    with open(os.path.join(agent_folder, "requirements.txt"), "w") as f:
        f.write("slackagents==0.0.1\npython-dotenv\n")
    # Create app.py
    app_py = """
from slackagents import AutoSlackAgent
from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())

if __name__ == "__main__":
    configuration_path = os.getenv("CONFIG_PATH")
    agent = AutoSlackAgent.from_config(config=configuration_path)
    agent.run()
""".strip()
    with open(os.path.join(agent_folder, "app.py"), "w") as f:
        f.write(app_py)

    # Create basic tool example
    tools_init = """
from slackagents import FunctionTool
from .example_tool import example_tool

example_tool = FunctionTool.from_function(example_tool)

__all__ = ["example_tool"]
""".strip()
    with open(os.path.join(agent_folder, "tools", "__init__.py"), "w") as f:
        f.write(tools_init)
    example_tool = """def example_tool(input: str) -> str:
    \"\"\"An example tool that echoes the input.
    
    :param input: The input string
    :type input: string
    :return: The echoed input
    :rtype: string
    \"\"\"
    return f"Echo: {input}"
    """.strip()
    with open(os.path.join(agent_folder, "tools", "example_tool.py"), "w") as f:
        f.write(example_tool)
    # Create .env file
    env_content = f"""
#=============================================================#
#                   SlackAgents Configuration                 #
#=============================================================#
# Please refer to the reference documentation for assistance  #
# with configuring your SlackAgents environment. The guide is #
# available both online and within your local SlackAgents     #
#=============================================================#


#============#
# Config     #
#============#
CONFIG_PATH=config.yaml
""".strip()
    with open(os.path.join(agent_folder, ".env"), "w") as f:
        f.write(env_content)
    # Add agent to slackagents_config.json
    bot = {
        "id": app_id,
        "name": name,
        "description": description,
        "type": type,
        "folder": agent_folder,
        "created_at": datetime.now().isoformat(),
        "status": "inactive"
    }
    config.setdefault('agents', []).append(bot)
    save_config(config)
    click.echo(click.style("Agent created successfully!", fg="green", bold=True))
    logger.info(f"Agent \"{name}\" created")
    click.echo(click.style(f"Now, you can start implementing the agent tools in the {agent_folder}/tools folder!", fg="green", bold=True))