from multiprocessing import Process, Queue
from slackagents.slack.handler import SlackChannelHandler
from agents.customer_service_agent import customer_service_agent
from agents.logistics_agent import logistics_agent
from agents.sales_agent import sales_agent
from agents.slack_bolt_id import customer_service_bolt_config, logistics_bolt_config, sales_agent_bolt_config


if __name__ == "__main__":
    # Create handlers for each agent
    customer_service_handler = SlackChannelHandler(customer_service_bolt_config, customer_service_agent)
    customer_service_handler.run()