import os
from slackagents.tools.base import ToolCall
from slackagents.tools.function_tool import FunctionTool
from slackagents.tools.utils import generate_function_definition_from_openapi_spec
from slackagents.tools.schema import APIKeyParams, BearerTokenParams, BasicAuthParams, AuthType
from typing import Any, Dict, Optional
from pydantic import Field

import json
import requests

class OpenAPITool(FunctionTool):
    """Class for OpenAPI-based tools."""
    
    openapi_spec: Dict = Field(
        default={}, description="The OpenAPI specification for the API."
    )
    base_url: str = Field(
        default="", description="The base URL for the API."
    )
    auth_type: AuthType = Field(
        default=AuthType.NO_AUTH, description="The type of authentication to use."
    )
    api_name: str = Field(
        default="", description="The name of the API for retrieving auth information."
    )

    def __init__(
        self, 
        name: str, 
        openapi_spec: Dict,
        auth_type: AuthType = AuthType.NO_AUTH,
        auth_key_prefix: Optional[str] = None,
        auth_params: Optional[Dict[str, str]] = None
    ):
        function_definition = generate_function_definition_from_openapi_spec(openapi_spec)
        super().__init__(name=name, function=function_definition, callback=self._execute_api_call)
        self.openapi_spec = openapi_spec
        self.base_url = self._get_base_url_from_spec()
        self.auth_type = auth_type
        self.api_name = auth_key_prefix or self.name
        self._auth_params = auth_params

    def _get_auth_params(self) -> Dict[str, str]:
        """Retrieve authentication parameters from instance or environment variables."""
        if self._auth_params:
            return self._auth_params

        prefix = f"{self.api_name.upper()}_"
        
        if self.auth_type == AuthType.API_KEY:
            return {
                "key_name": os.environ.get(f"{prefix}API_KEY_NAME", "api_key"),
                "key_value": os.environ.get(f"{prefix}API_KEY_VALUE"),
                "key_in": os.environ.get(f"{prefix}API_KEY_IN", "header")
            }
        elif self.auth_type == AuthType.BEARER_TOKEN:
            return {"token": os.environ.get(f"{prefix}BEARER_TOKEN")}
        elif self.auth_type == AuthType.BASIC_AUTH:
            return {
                "username": os.environ.get(f"{prefix}BASIC_AUTH_USERNAME"),
                "password": os.environ.get(f"{prefix}BASIC_AUTH_PASSWORD")
            }
        else:
          return {}

    def _apply_auth(self, request_kwargs: Dict[str, Any]):
        """Apply authentication to the request."""
        auth_params = self._get_auth_params()
        
        if self.auth_type == AuthType.API_KEY:
            try:
                api_key_params = APIKeyParams(**auth_params)
            except Exception as e:
                raise ValueError(f"Invalid API key parameters: {str(e)}")
            key_name = api_key_params.key_name
            key_value = api_key_params.key_value
            key_in = api_key_params.key_in
            if key_in == "header":
                request_kwargs.setdefault("headers", {})[key_name] = key_value
            elif key_in == "query":
                request_kwargs.setdefault("params", {})[key_name] = key_value
        elif self.auth_type == AuthType.BEARER_TOKEN:
            try:
                bearer_token_params = BearerTokenParams(**auth_params)
            except Exception as e:
                raise ValueError(f"Invalid bearer token parameters: {str(e)}")
            token = bearer_token_params.token
            request_kwargs.setdefault("headers", {})["Authorization"] = f"Bearer {token}"
        elif self.auth_type == AuthType.BASIC_AUTH:
            try:
                basic_auth_params = BasicAuthParams(**auth_params)
            except Exception as e:
                raise ValueError(f"Invalid basic auth parameters: {str(e)}")
            username = basic_auth_params.username
            password = basic_auth_params.password
            request_kwargs["auth"] = (username, password)
            
    def _get_base_url_from_spec(self) -> str:
        """Extract the base URL from the OpenAPI specification."""
        servers = self.openapi_spec.get("servers", [])
        if servers:
            return servers[0].get("url", "")
        return ""
    
    def _execute_api_call(self, **kwargs) -> Any:
        """Execute the API call based on the OpenAPI specification."""
        paths = self.openapi_spec.get("paths", {})
        path, path_item = next(iter(paths.items()))
        method, operation = next(iter(path_item.items()))
        
        url = f"{self.base_url}{path}"
        
        # Replace path parameters
        for param in operation.get("parameters", []):
            if param["in"] == "path":
                url = url.replace(f"{{{param['name']}}}", str(kwargs.pop(param["name"], "")))
        
        # Prepare request kwargs
        request_kwargs = {"params": kwargs}
        
        # Apply authentication
        self._apply_auth(request_kwargs)
        
        # Make the API call
        response = requests.request(method, url, **request_kwargs)
        
        # Return the response
        try:
            return response.json()
        except json.JSONDecodeError:
            return response.text
      
    def execute(self, tool_call: ToolCall) -> Any:
      """Execute the tool's functionality."""
      return self._execute_api_call(**tool_call.arguments)

if __name__ == "__main__":
    openapi_spec = {
      "openapi": "3.0.3",
      "info": {
        "title": "Chronicling America Title Search API",
        "description": "API for searching titles in the Chronicling America newspaper archive.",
        "version": "1.0.0"
      },
      "servers": [
        {
          "url": "https://chroniclingamerica.loc.gov"
        }
      ],
      "paths": {
        "/search/titles/results/": {
          "get": {
            "summary": "Search newspaper titles",
            "description": "Retrieve newspaper titles that match specified search terms.",
            "parameters": [
              {
                "name": "terms",
                "in": "query",
                "description": "The search term or phrase for querying newspaper titles.",
                "required": True,
                "schema": {
                  "type": "string",
                  "example": "oakland"
                }
              },
              {
                "name": "format",
                "in": "query",
                "description": "The format of the response.",
                "required": True,
                "schema": {
                  "type": "string",
                  "enum": ["json", "xml"],
                  "example": "json"
                }
              },
              {
                "name": "page",
                "in": "query",
                "description": "Page number for paginated results.",
                "required": True,
                "schema": {
                  "type": "integer",
                  "example": 5
                }
              }
            ],
            "responses": {
              "200": {
                "description": "A list of newspaper titles that match the search query.",
                "content": {
                  "application/json": {
                    "schema": {
                      "type": "object",
                      "properties": {
                        "totalItems": {
                          "type": "integer",
                          "description": "Total number of items found.",
                          "example": 100
                        },
                        "startIndex": {
                          "type": "integer",
                          "description": "The index at which the current page of results starts.",
                          "example": 40
                        },
                        "itemsPerPage": {
                          "type": "integer",
                          "description": "The number of items returned per page.",
                          "example": 20
                        },
                        "items": {
                          "type": "array",
                          "description": "List of newspaper titles.",
                          "items": {
                            "type": "object",
                            "properties": {
                              "title": {
                                "type": "string",
                                "description": "Title of the newspaper.",
                                "example": "The Oakland Tribune"
                              },
                              "id": {
                                "type": "string",
                                "description": "Identifier for the newspaper.",
                                "example": "sn85042462"
                              },
                              "place_of_publication": {
                                "type": "string",
                                "description": "Location where the newspaper is published.",
                                "example": "Oakland, Calif."
                              },
                              "start_year": {
                                "type": "integer",
                                "description": "The year the newspaper started publication.",
                                "example": 1874
                              },
                              "end_year": {
                                "type": "integer",
                                "description": "The year the newspaper ended publication or null if still ongoing.",
                                "example": 2016
                              }
                            }
                          }
                        }
                      }
                    }
                  }
                }
              },
              "400": {
                "description": "Bad request due to invalid parameter values."
              },
              "500": {
                "description": "Internal server error."
              }
            }
          }
        }
      }
    }
    tool = OpenAPITool(name="get_historical_american_newspapers", openapi_spec=openapi_spec, auth_type=AuthType.NO_AUTH)
    print(tool.info)
    tool_call = ToolCall(name="get_historical_american_newspapers", arguments={"terms": "oakland", "format": "json", "page": 5})
    print(tool.execute(tool_call))