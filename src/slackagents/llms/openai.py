import os
from typing import Dict, List, Optional, Type
from pydantic import BaseModel
from openai import OpenAI

from slackagents.llms.base import BaseLLM, BaseLLMConfig

class OpenAILLM(BaseLLM):
    def __init__(self, config: BaseLLMConfig):
        super().__init__()
        self.config = config

        if not self.config.model:
            self.config.model = "gpt-4o"

        if os.environ.get("OPENROUTER_API_KEY"):  # Use OpenRouter
            self.client = OpenAI(
                api_key=os.environ.get("OPENROUTER_API_KEY"),
                base_url=self.config.openrouter_base_url,
            )
        else:
            api_key = os.getenv("OPENAI_API_KEY") or self.config.api_key
            self.client = OpenAI(api_key=api_key)

    def _parse_response(self, response, tools, response_format):
        """
        Process the response based on whether tools are used or not.

        Args:
            response: The raw response from API.
            tools: The list of tools provided in the request.
            response_format: The format of the response.

        Returns:
            str or dict: The processed response.
        """
        if response_format:
            return response.choices[0].message.parsed
        elif tools:
            processed_response = {
                "content": response.choices[0].message.content,
            }

            if response.choices[0].message.tool_calls:
                processed_response["tool_calls"] = []
                for tool_call in response.choices[0].message.tool_calls:
                    processed_response["tool_calls"].append(
                        tool_call.model_dump()
                    )

            return processed_response
        else:
            return {"content": response.choices[0].message.content}

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict]] = None,
        tool_choice: str = "auto",
        response_format: Optional[Type[BaseModel]] = None,
    ):
        """
        Generate a response based on the given messages using OpenAI.

        Args:
            messages (list): List of message dicts containing 'role' and 'content'.
            response_format (Subclass of pydantic BaseModel class): Format of the response. Defaults to None.
            tools (list, optional): List of tools that the model can call. Defaults to None.
            tool_choice (str, optional): Tool choice method. Defaults to "auto".

        Returns:
            str: The generated response.
        """
        params = {
            "model": self.config.model,
            "messages": messages,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
            "top_p": self.config.top_p,
        }

        if os.getenv("OPENROUTER_API_KEY"):
            openrouter_params = {}
            if self.config.models:
                openrouter_params["models"] = self.config.models
                openrouter_params["route"] = self.config.route
                params.pop("model")

            if self.config.site_url and self.config.app_name:
                extra_headers = {
                    "HTTP-Referer": self.config.site_url,
                    "X-Title": self.config.app_name,
                }
                openrouter_params["extra_headers"] = extra_headers

            params.update(**openrouter_params)

        if response_format:
            if not isinstance(response_format, type):
                raise TypeError("response_format must be a class, not an instance of another type.")
            if not issubclass(response_format, BaseModel):
                raise TypeError("response_format must be a subclass of Pydantic BaseModel.")
            params["response_format"] = response_format
        if tools:
            params["tools"] = tools
            params["tool_choice"] = tool_choice

        completion_method = (
            self.client.beta.chat.completions.parse
            if response_format
            else self.client.chat.completions.create
        )

        response = completion_method(**params)
        return self._parse_response(response, tools, response_format)
