import os
import click
import logging
from slackagents.cli.config import load_config, save_config
import psutil
import signal

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)
    
def stop_agent(app_id):
    """Stop a running Slack agent with APP_ID."""
    config = load_config()
    bot = next((b for b in config.get("agents", []) if b["id"] == app_id), None)
    if bot: 
        agent_name = bot["name"]
        pid = bot.get("pid")
        
        if not pid:
            click.echo(click.style(f"No running process found for agent: {agent_name}", fg="yellow"))
            return
            
        try:
            process = psutil.Process(pid)
            if os.name == 'nt':  # Windows
                process.terminate()
            else:  # Unix-like systems
                # Kill the entire process group
                os.killpg(os.getpgid(pid), signal.SIGTERM)
    
            # Remove PID from config
            bot.pop("pid", None)
            bot["status"] = "inactive"
            save_config(config)

            click.echo(click.style(f"Agent {agent_name} stopped successfully!", fg="green"))
        except psutil.NoSuchProcess:
            click.echo(click.style(f"Process {pid} not found. Agent may have already stopped.", fg="yellow"))
            bot.pop("pid", None)
            save_config(config)
        except Exception as e:
            click.echo(click.style(f"Error stopping agent: {str(e)}", fg="red"))
            logger.error(f"Failed to stop agent \"{agent_name}\": {str(e)}")
    else:
        click.echo(click.style(f"Agent with APP_ID \"{app_id}\" not found", fg="red"))
        logger.error(f"Agent with APP_ID \"{app_id}\" not found")