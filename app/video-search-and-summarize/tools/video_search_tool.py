import json
from youtubesearchpython import VideosSearch
from slackagents import FunctionTool


def video_search(
    query: str,
    max_results: int=3
) -> str:
    """A tool to search videos on youtube.com
    :param query: the query to be used for searching videos
    :type query: string
    :param max_results: The maximum number of results to return
    :type max_results: number
    :return: a string in json format
    :rtype: string
    """
    videos_search = VideosSearch(
        query=query, 
        limit=max_results, 
        region='US', 
        language='en'
    )
    results = videos_search.result()
    filtered_results = [
    {
        "title": video["title"],
        "link": video["link"],
        "duration": video["duration"],
        "views": video.get("viewCount", {}).get("text", "N/A")
    }
    for video in results["result"]
    ]
    filtered_results_json = json.dumps(filtered_results, indent=4)
    return filtered_results_json


video_search_tool = FunctionTool.from_function(video_search)
# print(f"Video Search Tool: {json.dumps(video_search_tool.info, indent=4)}")