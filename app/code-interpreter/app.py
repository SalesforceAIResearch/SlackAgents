from slackagents import AutoSlackAgent
from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())

if __name__ == "__main__":
    configuration_path = os.getenv("CONFIG_PATH")
    agent = AutoSlackAgent.from_config(config=configuration_path)
    agent.run()