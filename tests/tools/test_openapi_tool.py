import unittest
from unittest.mock import patch, MagicMock
import os
from slackagents.tools.openapi_tool import OpenAPITool
from slackagents.tools.schema import AuthType
from slackagents.tools.base import ToolCall

class TestOpenAPITool(unittest.TestCase):

    def setUp(self):
        self.openapi_spec = {
            "openapi": "3.0.3",
            "info": {"title": "Test API", "version": "1.0.0"},
            "servers": [{"url": "https://api.example.com"}],
            "paths": {
                "/test": {
                    "get": {
                        "parameters": [
                            {"name": "param1", "in": "query", "schema": {"type": "string"}},
                            {"name": "param2", "in": "query", "schema": {"type": "integer"}}
                        ]
                    }
                }
            }
        }

    def test_init(self):
        tool = OpenAPITool(name="test_tool", openapi_spec=self.openapi_spec)
        self.assertEqual(tool.name, "test_tool")
        self.assertEqual(tool.base_url, "https://api.example.com")
        self.assertEqual(tool.auth_type, AuthType.NO_AUTH)

    def test_get_auth_params_api_key(self):
        with patch.dict(os.environ, {"TEST_TOOL_API_KEY_NAME": "api_key", "TEST_TOOL_API_KEY_VALUE": "12345"}):
            tool = OpenAPITool(name="test_tool", openapi_spec=self.openapi_spec, auth_type=AuthType.API_KEY)
            auth_params = tool._get_auth_params()
            self.assertEqual(auth_params, {"key_name": "api_key", "key_value": "12345", "key_in": "header"})

    def test_get_auth_params_bearer_token(self):
        with patch.dict(os.environ, {"TEST_TOOL_BEARER_TOKEN": "token123"}):
            tool = OpenAPITool(name="test_tool", openapi_spec=self.openapi_spec, auth_type=AuthType.BEARER_TOKEN)
            auth_params = tool._get_auth_params()
            self.assertEqual(auth_params, {"token": "token123"})

    @patch('requests.request')
    def test_execute_api_call(self, mock_request):
        mock_response = MagicMock()
        mock_response.json.return_value = {"result": "success"}
        mock_request.return_value = mock_response

        tool = OpenAPITool(name="test_tool", openapi_spec=self.openapi_spec)
        result = tool._execute_api_call(param1="test", param2=123)

        mock_request.assert_called_once_with(
            "get",
            "https://api.example.com/test",
            params={"param1": "test", "param2": 123}
        )
        self.assertEqual(result, {"result": "success"})

    @patch('requests.request')
    def test_execute(self, mock_request):
        mock_response = MagicMock()
        mock_response.json.return_value = {"result": "success"}
        mock_request.return_value = mock_response

        tool = OpenAPITool(name="test_tool", openapi_spec=self.openapi_spec)
        tool_call = ToolCall(name="test_tool", arguments={"param1": "test", "param2": 123})
        result = tool.execute(tool_call)

        mock_request.assert_called_once_with(
            "get",
            "https://api.example.com/test",
            params={"param1": "test", "param2": 123}
        )
        self.assertEqual(result, {"result": "success"})

    @patch('requests.request')
    def test_execute_api_call_with_auth(self, mock_request):
        mock_response = MagicMock()
        mock_response.json.return_value = {"result": "success"}
        mock_request.return_value = mock_response

        with patch.dict(os.environ, {"TEST_TOOL_API_KEY_NAME": "api_key", "TEST_TOOL_API_KEY_VALUE": "12345"}):
            tool = OpenAPITool(name="test_tool", openapi_spec=self.openapi_spec, auth_type=AuthType.API_KEY)
            result = tool._execute_api_call(param1="test", param2=123)

        mock_request.assert_called_once_with(
            "get",
            "https://api.example.com/test",
            params={"param1": "test", "param2": 123},
            headers={"api_key": "12345"}
        )
        self.assertEqual(result, {"result": "success"})

if __name__ == '__main__':
    unittest.main()