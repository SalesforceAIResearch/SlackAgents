import click
import json
from tabulate import tabulate
import logging
from slackagents.cli.config import load_config

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def list_agents(verbose, format):
    """List all available Slack bots."""
    config = load_config()
    bots = config.get("agents", [])
    if format == "json":
        click.echo(json.dumps(bots, indent=2))
    else:
        headers = ["APP_ID", "Name", "Status", "Type", "PID"] if not verbose else ["APP_ID", "Name", "Status", "Type", "PID", "Folder", "Description", "Created At"]
        table_data = []
        for bot in bots:
            if "pid" in bot:
                pid = bot["pid"]
            else:
                pid = "N/A"
            row = [bot["id"], bot["name"], bot["status"], bot["type"], pid]
            if verbose:
                row.extend([bot["folder"], bot["description"], bot["created_at"]])
            table_data.append(row)
        click.echo(tabulate(table_data, headers=headers, tablefmt="mixed_grid", numalign="center", stralign="left"))
    logger.info("Bot list displayed")