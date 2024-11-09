"""Command-line interface for slackagents."""

import click
import os
import logging
from slackagents.cli.config import load_config
from slackagents.cli.create_agent import create_agent
from slackagents.cli.list_agent import list_agents
from slackagents.cli.start_agent import start_agent
from slackagents.cli.stop_agent import stop_agent
from slackagents.cli.delete_agent import delete_agent
from slackagents.cli.add_agent import add_agent
# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class AliasedGroup(click.Group):
    r"""
    The AliasedGroup class is a custom implementation that extends Click"s Group class 
    to provide command aliasing/partial matching functionality. When a user types a 
    partial command name, it tries to match it against available commands.
    """
    def get_command(self, ctx, cmd_name):
        rv = click.Group.get_command(self, ctx, cmd_name)
        if rv is not None:
            return rv
        matches = [x for x in self.list_commands(ctx) if x.startswith(cmd_name)]
        if not matches:
            return None
        elif len(matches) == 1:
            return click.Group.get_command(self, ctx, matches[0])
        ctx.fail(f"Too many matches: {", ".join(sorted(matches))}")

@click.group(cls=AliasedGroup)
@click.version_option()
def cli():
    """
    \b
    ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
    ┃                                                  ┃
    ┃   SlackAgents CLI                                ┃
    ┃   Your Slack AI Agent Management Tool            ┃
    ┃                                                  ┃
    ┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
    ┃Features:                                         ┃
    ┃                                                  ┃
    ┃  🤖 Create and manage Slack AI agents            ┃
    ┃  🔧 Configure advanced agent behaviors           ┃
    ┃  📊 Monitor real-time agent activities           ┃
    ┃  🚀 Deploy agents to your Slack workspace        ┃
    ┃                                                  ┃
    ┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
    ┃  © 2024 Salesforce AI Research                   ┃
    ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

    Type "slackagents --help" to see all available commands.
    """
    pass

# Create Agent
@cli.command()
@click.option("--app_id", prompt="Slack App ID", required=True, help="Slack App ID")
@click.option("--bot_token", prompt="Slack Bot Token", required=True, help="Slack Bot Token")
@click.option("--app_token", prompt="Slack App Token", required=True, help="Slack App Token")
@click.option("--name", prompt="Agent Name", required=True, help="Name of the Slack AI agent")
@click.option("--description", prompt="Agent Description", required=True, help="Short description of the agent")
@click.option("--type", prompt="Agent Type", required=True, help="Type of the agent", type=click.Choice(["SlackAssistant", "SlackDMAssistant", "SlackChannelAssistant", "SlackWorkflow"]), default="SlackAssistant")
@click.option("--root_folder", prompt="Root Directory", required=True, help="Root directory for this agent", default=f"{os.getcwd()}")

def create(app_id, bot_token, app_token, name, description, type, root_folder):
    """Create a new Slack agent."""
    create_agent(app_id, bot_token, app_token, name, description, type, root_folder)

# List Agents
@cli.command()
@click.option("--verbose", "-v", is_flag=True, help="Show detailed information")
@click.option("--format", type=click.Choice(["table", "json"]), default="table", help="Output format")

def list(verbose, format):
    """List all available Slack agents with APP_ID, Name, Status, Type, etc."""
    list_agents(verbose, format)

# Add Agent
@cli.command()
@click.argument("folder_path")
def add(folder_path):
    """Add a Slack agent with folder path."""
    add_agent(folder_path)

# Start Agent
@cli.command()
@click.argument("app_id")

def start(app_id):
    """Start a Slack agent with APP_ID."""
    start_agent(app_id)

# Stop Agent
@cli.command()
@click.argument("app_id")
def stop(app_id):
    """Stop a running Slack agent with APP_ID."""
    stop_agent(app_id)

# Delete Agent
@cli.command()
@click.argument("app_id")
@click.confirmation_option(prompt="Are you sure you want to delete this project entirely?")
def delete(app_id):
    """Delete a Slack agent with APP_ID."""
    delete_agent(app_id)
if __name__ == "__main__":
    cli(prog_name="slackagents")  # pragma: no cover
