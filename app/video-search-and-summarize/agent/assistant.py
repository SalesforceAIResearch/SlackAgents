from slackagents import Assistant, OpenAILLM, BaseLLMConfig
from tools.video_search_tool import video_search_tool
from tools.video_summarization_tool import video_summarization_tool


assistant = Assistant(
    name="Video Assistant",
    desc="An assistant that can help search youtube video and return basic information and summarization of the videos",
    llm=OpenAILLM(BaseLLMConfig(model="gpt-4o")),
    tools=[video_search_tool, video_summarization_tool],
    system_prompt=(
        "You are an AI assistant that helps search YouTube videos and return a list of videos with basic information. "
        "First, provide the user with the list of videos including title, YouTube URL, duration, and number of views. "
        "Then, ask the user to confirm which video they would like summarized. "
        "Always ensure to ask for user confirmation before summarizing any video."
    ),
    verbose=True # whether to print the assistant's tool request and response messages to the console
)

