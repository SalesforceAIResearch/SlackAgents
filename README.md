<!-- <div style="display: flex; align-items: center; justify-content: center">
  <img src="imgs/icon.png" width="100px" style="margin-right: 10px;" />
  <h1 style="text-align: center;">SlackAgents: Scalable AI Agents Deployment in Your Workspaces</h1>
</div> -->



<p align="left" style="white-space: nowrap;">
  <img align="left" src="imgs/icon.png" width="100px" style="margin-right: 20px; vertical-align: middle;" />
  <h1 style="margin: 0; display: inline-block; vertical-align: middle;">SlackAgents: Scalable Collaboration of Multiple AI Agents in Workspaces</h1>
</p>



<div align="center">

  ![Python 3.12+](https://img.shields.io/badge/Python-3.12%2B-brightgreen.svg)
  [![PyPI - Python Version](https://img.shields.io/pypi/v/slackagents.svg?color=brightgreen)](https://pypi.org/project/slackagents)
  [![License](https://img.shields.io/badge/License-Apache-green.svg)]()
  [![GitHub star chart](https://img.shields.io/github/stars/SalesforceAIResearch/slackagents?style=social)](https://star-history.com/#your-repo/slackagents)

</div>

<p align="center">
  <a href="#-installation">Installation</a> |
  <a href="#-quick-start">Quick Start</a> |
  <a href="#-multi-agent-collaboration-in-a-slack-channel">Multi-Agent Collaboration</a> |
  <a href="#-command-line-interface-cli">CLI</a> |
  <a href="#-build-your-own-agent-and-workflow">Build Your Own Workflow</a> |
  <a href="#-examples">Examples</a>
</p>

---


🤖 **SlackAgents** is a flexible library designed to facilitate the deployment of AI agents within your [Slack](https://slack.com/) workspaces. It supports scalable multi-agent collaboration and management, making it an ideal choice for organizations looking to enhance their Slack environments with agentic automation.

## 🌟 Key Features

- **Scalable Multi-Agent Collaboration**: Easily manage and deploy multiple agents within Slack.
- **Integration with OpenAI**: Leverage powerful language models to enhance agent capabilities.
- **Customizable and Extensible**: Build custom tools and workflows tailored to your needs.
- **User-Friendly CLI**: Simplifies agent management with intuitive commands.

## 📁 Repository Overview

The repository is structured as follows:

- **src/slackagents**: Contains the main implementation of the SlackAgents library.
- **app**: Includes Slack application-specific code and configurations.
- **examples**: Provides example scripts and notebooks to demonstrate the usage of SlackAgents.
- **tests**: Contains unit tests for the library.

## 🔧 Installation

Create a new conda environment:

```bash
conda create -n slackagents python=3.12 -y
conda activate slackagents
```

To install the package, use pip:

```bash
pip install slackagents
```

For development purposes, we recommend you install the package using poetry:

```bash
pip install poetry
poetry install
```
<!-- ## 🌐 Environment Setup -->

Finally, set the necessary environment variables by exporting them in your terminal session. For example:

```bash
export OPENAI_API_KEY=your_openai_api_key
```

## 🚀 Quick Start

Follow these steps to quickly set up and start using `SlackAgents` to create an assistant agent in Slack:

### 1. Create Your Slack App

We recommend using the [slack manifest](https://api.slack.com/reference/manifests) to setup the slack app and get the bot token and app token. We have a sample manifest in the [`app/your_first_slack_assistant`](app/your_first_slack_assistant) folder. You can update the manifest with your own agent name and description. We have updated the `display_name` and `name` fields when loading the manifest to match your agent's name as in the `agent_config.json` file.
First get your app config token at (config-tokens)[https://api.slack.com/reference/manifests#config-tokens] and export the token as 
```bash
export SLACK_APP_CONFIG_TOKEN=xoxe.xoxp...
```

Then create the slack app by running the following command:

```bash
cd app/your_first_slack_assistant
python create_slack_app.py
```

Now we have created a slack app and saved its app id in the `slack_bolt_id.json` file. You can view this app in the [slack app dashboard](https://api.slack.com/apps).

We Follow the [Slack Bolt Python Getting Started Guide](https://tools.slack.dev/bolt-python/getting-started) to set up your Slack app. Checking the following sections:
- [Tokens and Installing Apps](https://tools.slack.dev/bolt-python/getting-started#tokens-and-installing-apps)
- [Setting Up Events](https://tools.slack.dev/bolt-python/getting-started#setting-up-events)

After completing these steps, you should have the following credentials:
- **App ID**: Found in the *Basic Information* section of [your app's dashboard](https://api.slack.com/apps).
- **SLACK_BOT_TOKEN**: xoxb-...
- **SLACK_APP_TOKEN**: xapp-...

Make sure to add the following scopes to your app: `groups:read`, `channels:history`, `channels:read`, `im:history`, `chat:write`, `users:read`, `im:read`, and `app_mentions:read`.

### 2. Configure Your Slack Bolt ID

Update the [`slack_bolt_id.json`](app/your_first_slack_assistant/slack_bolt_id.json) file with your **App ID**, **SLACK_BOT_TOKEN**, and **SLACK_APP_TOKEN**.

### 3. Start Your Agent

To launch your assistant agent, execute the following command:

```bash
python my_agent.py
```

Read me the tutorial [here](./examples/slack_agent/build_app_with_manifest.ipynb) for more details.

### 4. Interact with Your Agent in Slack

Once your agent is running, you can start chatting with it directly in Slack. Simply send messages to the app in Slack, and your agent will respond accordingly. Sometimes the message window will not be turned on immediately once you create the app, so please be patient and shut-down and restart slack after a few minutes. 

![First DM Chat](/examples/slack_agent/img/first_dm.png)

## 🤝 Multi-Agent Collaboration in a Slack Channel

This guide will walk you through setting up multi-agent collaboration in a Slack channel using **SlackAgents**. Follow the steps below to configure the bot, set up colleagues, and enable collaboration.

### 1. Set Up Bolt Configuration

One of the key features of **SlackAgents** is its ability to interact with users in a Slack channel. To enable this feature, you need to:

#### a. Invite the Bot to the Channel
First, invite your bot to the channel where you want it to participate. This allows the bot to listen and respond to messages from users.

#### b. Obtain the Bot's `user_id`
To properly configure the bot, you'll need its `user_id` within the channel. Here's how to get it:
1. Click on the bot's icon in the channel.
2. Look for the **Member ID**, which will appear in the format `UXXXXXXXXX`.

This `user_id` is crucial as it will be used as one of the dictionary keys in your configuration. For more details on how to retrieve and use `user_id`, refer to [this link](https://api.slack.com/enterprise#user_ids) and [this link](https://api.slack.com/methods/users.info).

#### c. Update the Bot's ID in Code
Once you have obtained the `user_id`, update the **slack_bolt_id.py** file by replacing the placeholder with the actual `user_id` you retrieved.

### 2. Set Up Colleagues for Multi-Agent Collaboration

To enable multi-agent collaboration within a Slack channel, you need to define "colleagues" for your agent. This setup allows multiple agents (or users) to interact with each other within the same workspace.

#### a. Define Colleagues
The colleagues' configuration is a dictionary that maps each colleague's `user_id` to their name and description. This dictionary sets up a collaborative environment for agents within the channel.

- Ensure that your own `user_id` and those of other users who wish to interact with the agent are included in the **get_channel_user_ids_and_names** function.
- If you want your agent to collaborate with other agents, include their `user_id` in this dictionary.

For an enhanced collaboration experience, provide detailed information about each colleague in their corresponding description field.

#### Example Colleagues Dictionary:
```python
colleagues = {
    "UXXXXXXXXX": {"name": "AgentA", "description": "Handles customer queries"},
    "UYYYYYYYYY": {"name": "AgentB", "description": "Specializes in technical support"}
}
```

### 3. Restarting Your Agent

After updating your configuration, ensure that any previously running instance of your agent is shut down. Then, restart it using the following command:

```bash
python examples/slack_agent/slack_agent_run.py
```

### 4. Start Chatting with Your Agent in Slack

Once everything is set up, you can now interact with your agent by mentioning it directly in the Slack channel. The agent will respond based on its configuration and collaborate with other agents or users as specified.


## 💻 Command Line Interface (CLI)

SlackAgents offers a command-line interface to facilitate the management of AI agents within your Slack workspace. The following commands are available:

### Getting Started

The CLI is super simple to use:

```bash
slackagents [COMMAND] [OPTIONS]
```

Need help? Just run `slackagents` in terminal to see all available commands!

### Available Commands

#### Create a New Agent

```bash
slackagents create
```

This interactive wizard will guide you through creating a new agent step by step. Perfect for getting started!

#### Add an Existing Agent

```bash
slackagents add [FOLDER_PATH]
```

This command will add an existing agent in a standard SlackAgents app folder structure to the CLI for management. `FOLDER_PATH` is the relative or absolute path to the folder that contains the agent's `app.py` file.

#### List Your Agents

```bash
slackagents list
```

See all your agents at a glance! This command shows: APP_ID, Agent Name, Current Status, Agent Type, and more in `--verbose` mode! Users should use this command to monitor the status of the agents and get the `APP_ID` of the agents they want to start or stop.

#### Start an Agent

```bash
slackagents start [APP_ID]
```

Got your APP_ID from the list command? Fire up your agent with this simple command!

#### Stop an Agent

```bash
slackagents stop [APP_ID]
```

Need to pause an agent? No problem! Just stop it with this command.

#### Delete an Agent

```bash
slackagents delete [APP_ID]
```

Want to remove an agent completely? This command will clean up everything related to the specified agent.

### Pro Tips

- Always start with `slackagents list` to get an overview of your agents
- Use the `--help` flag with any command for detailed information
- Keep track of your APP_IDs - they're your keys to managing specific agents!

Here are my suggestions for improving the section, including a better name and some additional refinements:


## 🧑‍💻 Build Your Own Agent and Workflow

This section provides an overview of how to set up individual agents and create complex workflows using `SlackAgents`. You'll learn how to configure assistants for specific tasks and combine them into workflows that automate multi-step processes.

### 🤖 Assistant

Assistants are the core building blocks of `SlackAgents`. They are designed to interact with users and perform various tasks across channels and direct messages (DMs). Below is an example of an assistant that performs mathematical operations:

```python
from slackagents import Assistant, FunctionTool, OpenAILLM, BaseLLMConfig

def multiply(a: float, b: float) -> float:
    """Multiplies two numbers."""
    return a * b

# Create a tool from the multiply function
multiply_tool = FunctionTool.from_function(function=multiply)

# Initialize the LLM
llm_config = BaseLLMConfig(model="gpt-4o", temperature=0.7)
llm = OpenAILLM(config=llm_config)

# Create an assistant
assistant = Assistant(
    name="Math Assistant",
    desc="An assistant that can perform mathematical operations.",
    llm=llm,
    tools=[multiply_tool],
    verbose=True
)

# Interact with the assistant
response = assistant.chat("What's 5 times 7?")
print(response)
```

In this example:
- The `multiply` function is wrapped as a tool using `FunctionTool`.
- The assistant is powered by OpenAI's GPT model (`gpt-4o`) with a custom configuration.
- The assistant can now respond to mathematical queries in Slack or other channels.

### 🔄 Workflow Agent

The `WorkflowAgent` allows you to create complex workflows involving multiple agents. Each agent in the workflow performs specific tasks, and transitions define how agents pass information between each other.

Here's an example workflow for automating employee quarterly check-ins:

```python
from slackagents import Assistant, WorkflowAgent, FunctionTool
from slackagents.graph.execution_graph import ExecutionGraph, ExecutionTransition

# Define tools for each agent
def load_jira_record_tool(employee_id: str):
    # Implementation...

def write_tool(content: str, document_name: str):
    # Implementation...

def load_employee_calendar_tool(employee_id: str):
    # Implementation...

def send_calendar_invite_tool(employee_id: str, time_slot: str, meeting_title: str, notes: str):
    # Implementation...

def send_email_tool(employee_id: str, subject: str, body: str):
    # Implementation...

# Create agents with specific roles
data_agent = Assistant(
    name="Data Agent",
    desc="AI agent designed to load an employee's Jira record and generate a report for the quarterly check-in meeting.",
    tools=[
        FunctionTool.from_function(load_jira_record_tool),
        FunctionTool.from_function(write_tool),
    ],
    system_prompt="...",  # Define system prompt
)

calendar_agent = Assistant(
    name="Calendar Agent",
    desc="AI agent designed to load an employee's calendar and send the calendar invites",
    tools=[
        FunctionTool.from_function(load_employee_calendar_tool),
        FunctionTool.from_function(send_calendar_invite_tool)
    ],
    system_prompt="...",  # Define system prompt
)

email_agent = Assistant(
    name="Email Agent",
    desc="AI agent designed to send emails to employees",
    tools=[FunctionTool.from_function(send_email_tool)],
    system_prompt="...",  # Define system prompt
)

# Create execution graph
graph = ExecutionGraph()
graph.add_agent(data_agent)
graph.add_agent(calendar_agent)
graph.add_agent(email_agent)

# Define transitions between agents
graph.add_transition(
    ExecutionTransition(
        source_module=graph.get_module("Data Agent"), 
        target_module=graph.get_module("Calendar Agent"), 
        desc="When the report written to the employee's local directory, you should schedule the meeting with the employees."
    )
)

graph.add_transition(
    ExecutionTransition(
        source_module=graph.get_module("Calendar Agent"), 
        target_module=graph.get_module("Email Agent"), 
        desc="Once the meeting is scheduled, send email notifications."
    )
)

# Set initial agent in the workflow
graph.set_initial_module(graph.get_module("Data Agent"))

# Create WorkflowAgent for quarterly check-ins
quarterly_checkin_agent = WorkflowAgent(
    name="Quarterly Check-in Workflow",
    desc="Workflow designed to automate the employee quarterly check-in process",
    graph=graph,
    verbose=True
)

# Use the WorkflowAgent to start the process
response = quarterly_checkin_agent.chat("The quarterly check-in is due in a week. Please help prepare.")
print(response)
```

In this example:
- **Data Agent** loads Jira records and generates reports.
- **Calendar Agent** schedules meetings based on employee calendars.
- **Email Agent** sends notifications once meetings are scheduled.
- Transitions define when one agent passes control to another based on task completion.

### 📚 Main Modules and APIs

`SlackAgents` provides several key modules and APIs that form its core functionality. Here’s an overview of some of the most important ones:

| Module/API | Description | File Reference |
|------------|-------------|----------------|
| `Assistant` | A base class for creating AI assistants | `src/slackagents/agent/assistant.py` |
| `WorkflowAgent` | An agent designed for executing multi-step workflows | `src/slackagents/agent/workflow_agent.py` |
| `SlackAssistant` | An AI assistant integrated with Slack | `src/slackagents/agent/slack_assistant.py` |
| `SlackWorkflowAgent` | A workflow agent integrated with Slack | `src/slackagents/agent/slack_workflow_agent.py` |
| `SlackDMAgent` | An agent for handling direct messages in Slack | `src/slackagents/agent/slack_dm_agent.py` |
| `FunctionTool` | A tool for creating custom functions that agents can use | `src/slackagents/tools/function_tool.py` |
| `OpenAPITool` | A tool for integrating OpenAPI specifications | `src/slackagents/tools/openapi_tool.py` |
| `OpenAILLM` | An interface for OpenAI's language models | `src/slackagents/llms/openai.py` |
| `BaseLLMConfig` | A configuration class for language models | `src/slackagents/llms/openai.py` |

These modules and APIs provide a comprehensive toolkit for building AI-powered agents within Slack workspaces. Whether you're creating simple assistants or complex workflows, these components offer flexibility and power.

## 🔍 Examples

For more detailed examples, please check the `examples` folder in the repository. It contains notebooks demonstrating various use cases, including:

- Creating custom tools
- Using OpenAPI specifications
- Integrating with Slack
- Building workflow agents
- Automating employee quarterly check-ins

## 🧪 Tests

`unittests` is used to run our tests. You can run the following command to run the tests:

```bash
sh scripts/tests.sh
```

## 📦 Publish on PyPi

**Important**: Before publishing, edit `__version__` in [src/__init__](/src/__init__.py) to match the wanted new version.

```bash
poetry build
poetry publish
```

## 📞 Contact

For questions or suggestions, please reach out by submitting an issue or pull request, or send an email to the project maintainers.
