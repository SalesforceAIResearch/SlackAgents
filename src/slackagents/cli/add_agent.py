import os
import click
import logging
from slackagents.cli.config import load_config, save_config
import yaml
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def add_agent(folder_path):
    """Add a Slack agent with FOLDER_PATH."""
    config = load_config()
    # get absolute path
    folder_path = os.path.abspath(folder_path)
    app_py_path = os.path.join(folder_path, "app.py")
    if not os.path.exists(app_py_path):
        click.echo(click.style(f"No app.py found in {folder_path}", fg="red"))
        logger.error(f"No app.py found in {folder_path}")
        return
    else:
        config_yaml_path = os.path.join(folder_path, "config.yaml")
        if not os.path.exists(config_yaml_path):
            click.echo(click.style(f"No config.yaml found in {folder_path}", fg="red"))
            logger.error(f"No config.yaml found in {folder_path}")
            return
        else:
            click.echo(click.style(f"Adding agent from {folder_path}", fg="green"))
            logger.info(f"Adding agent from {folder_path}")
            with open(config_yaml_path, "r") as f:
                yaml_config = yaml.safe_load(f)
            app_id = yaml_config["slackConfig"]["id"]
            if app_id is None:
                click.echo(click.style(f"No id found in slackConfig in {config_yaml_path}", fg="red"))
                logger.error(f"No id found in slackConfig in {config_yaml_path}")
                return
            name = yaml_config["agentConfig"]["name"]
            description = yaml_config["agentConfig"]["desc"]
            type = yaml_config["agentConfig"]["type"]
            
            bot = {
                "id": app_id,
                "name": name,
                "description": description,
                "type": type,
                "folder": folder_path,
                "created_at": datetime.now().isoformat(),
                "status": "inactive"
            }
            config.setdefault('agents', []).append(bot)
            save_config(config)
            click.echo(click.style("Agent added successfully!", fg="green", bold=True))
            logger.info(f"Agent \"{name}\" added")