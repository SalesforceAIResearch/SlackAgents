import os
import serpapi
from dotenv import load_dotenv, find_dotenv
from typing import Dict

load_dotenv(find_dotenv())

def google_search(query: str) -> str:
    """Make a query to the Google search engine to receive a list of results.
    :param query: The query to be passed to Google search.
    :type query: str
    :return: The results of the google search query.
    :rtype: str
    """
    try:
        results = get_results(query)
        results = process_response(results)
    except Exception as e:
        return f"An error occurred: {e}"
    return results

def get_results(query: str) -> dict:
    """Run query through SerpAPI and return the raw result."""
    client = serpapi.Client(api_key=os.getenv("SERPAPI_API_KEY"))
    results = client.search({
        "q": query,
    })
    return results.as_dict()

def process_response(results: dict) -> str:
    output = {
        "answer_box": None,
        "organic_results": [],
    }
    if "answer_box" in results.keys():
        output["answer_box"] = results["answer_box"]
    
    if "organic_results" in results.keys():
        for result in results["organic_results"]:
            result_keys = result.keys()
            processed_result = { }
            if "title" in result_keys:
                processed_result["title"] = result["title"]
            if "source" in result_keys:
                processed_result["source"] = result["source"]
            if "link" in result_keys:
                processed_result["link"] = result["link"]
            if "snippet" in result_keys:
                processed_result["content"] = result["snippet"]
            if "rich_snippet" in result_keys:
                processed_result["content"] = processed_result["content"] + result["rich_snippet"]
            if "rich_snippet_table" in result_keys:
                processed_result["content"] = processed_result["content"] + result["rich_snippet_table"]
            output["organic_results"].append(processed_result)
    return output

if __name__ == "__main__":
    print(google_search("Weiran Yao Salesforce"))