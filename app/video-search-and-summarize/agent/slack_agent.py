from slackagents import SlackDMAgent
from slackagents.llms.base import BaseLLMConfig
from slackagents.llms.openai import OpenAILLM
from slackagents.commons.configuration_schemas import SlackAgentConfig
from tools.video_search_tool import video_search_tool
from tools.video_summarization_tool import video_summarization_tool

video_search_agent = SlackDMAgent(name="Video Assistant",
    desc="An assistant that can help search youtube video and return basic information and summarization of the videos",
    llm=OpenAILLM(BaseLLMConfig(model="gpt-4o")),
    tools=[video_search_tool, video_summarization_tool],
    system_prompt=(
        "You are an AI assistant that helps search YouTube videos and return a list of videos with basic information. "
        "Provide the user with the list of videos including title, YouTube URL, duration, and number of views. Always ensure to ask for user confirmation before summarizing any video."
        "when you greet the user you should always introduce yourself as a video assistant and ask for the user's query"
    ),
    verbose=True # whether to print the assistant's tool request and response messages to the console
)


