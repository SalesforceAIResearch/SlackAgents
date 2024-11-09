import os
import click
import logging
from slackagents.cli.config import load_config, save_config
from slackagents.cli.stop_agent import stop_agent
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def delete_agent(app_id):
    """Delete a Slack agent with APP_ID."""
    config = load_config()
    bots = config.get("agents", [])
    bot = next((b for b in bots if b["id"] == app_id), None)
    if bot:
        bot_name = bot["name"]
        # Stop the agent before deleting
        click.echo(f"Stopping agent {bot_name}...")
        stop_agent(app_id)
        click.echo(f"Deleting agent {bot_name}...")
        try:
            os.system(f"rm -rf {bot['folder']}")  # Using rm -rf to delete the entire folder
            bots.remove(bot)
            save_config(config)
            click.echo(click.style(f"Agent \"{bot_name}\" deleted successfully!", fg="green"))
            logger.info(f"Agent \"{bot_name}\" deleted")
        except Exception as e:
            click.echo(click.style(f"Error deleting agent: {str(e)}", fg="red"))
            logger.error(f"Failed to delete agent \"{bot_name}\": {str(e)}")
    else:
        click.echo(click.style(f"Agent with APP_ID \"{app_id}\" not found", fg="red"))
        logger.error(f"Agent with APP_ID \"{app_id}\" not found")