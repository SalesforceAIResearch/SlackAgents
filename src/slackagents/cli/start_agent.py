import os
import click
import logging
from slackagents.cli.config import load_config, save_config
import subprocess
import atexit
import time
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def start_agent(app_id):
    """Start a Slack agent with APP_ID."""
    config = load_config()
    bot = next((b for b in config.get("agents", []) if b["id"] == app_id), None)
    if bot:
        if bot["status"] == "active":
            click.echo(click.style(f"Agent \"{bot['name']}\" is already running!", fg="yellow"))
            logger.info(f"Agent \"{bot['name']}\" is already running!")
            return
        agent_name = bot["name"]
        agent_folder = bot["folder"]
        if os.path.exists(agent_folder):
            click.echo(click.style(f"Starting agent: {agent_name}", fg="yellow"))
            try:
                # Change to agent directory and run app.py in background
                os.chdir(agent_folder)
                log_file = open('slackagent.log', 'a', buffering=1)  # Use line buffering
                env = os.environ.copy()
                env['PYTHONUNBUFFERED'] = '1'  # Force Python to disable buffering
                
                if os.name == 'nt':  # Windows
                    process = subprocess.Popen(["python", "-u", "app.py"],  # Added -u flag
                                            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
                                            stdout=log_file,
                                            stderr=subprocess.STDOUT,
                                            env=env)
                else:  # Unix-like systems
                    process = subprocess.Popen(["python", "-u", "app.py"],  # Added -u flag
                                            stdout=log_file,
                                            stderr=subprocess.STDOUT,
                                            preexec_fn=os.setpgrp,
                                            env=env)
                # Register the log file to be closed when the parent process exits
                atexit.register(log_file.close)
                
                # Wait a moment and check if process is still running
                time.sleep(2)  # Give the process 2 seconds to start
                
                if process.poll() is None:  # Process is still running
                    # Store the PID in the config
                    bot["pid"] = process.pid
                    bot["status"] = "active"
                    save_config(config)
                    click.echo(click.style(f"Agent started successfully in background! (PID: {process.pid})", fg="green"))
                else:
                    click.echo(click.style("Agent failed to start - process terminated immediately", fg="red"))
                    logger.error(f"Agent \"{agent_name}\" failed to start - process terminated immediately")
                    return
                
            except Exception as e:
                click.echo(click.style(f"Error starting agent: {str(e)}", fg="red"))
                logger.error(f"Failed to start agent \"{agent_name}\": {str(e)}")
        else:
            click.echo(click.style(f"Agent folder \"{agent_folder}\" not found", fg="red"))
            logger.error(f"Agent folder \"{agent_folder}\" not found")
            return
    else:
        click.echo(click.style(f"Agent with APP_ID \"{app_id}\" not found", fg="red"))
        logger.error(f"Agent with APP_ID \"{app_id}\" not found")