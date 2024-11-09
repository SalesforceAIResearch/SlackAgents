import inspect
from docstring_parser import parse
from typing import Dict, Callable
from slackagents.tools.schema import FunctionDefinition
from slackagents.tools.base import BaseTool
def auto_cast_params(func, **params):
    # Get the function signature
    sig = inspect.signature(func)
    # Iterate over the function's parameters
    casted_params = {}
    for param_name, param in sig.parameters.items():
        expected_type = param.annotation
        
        # If there's a type annotation, attempt to cast
        if param_name in params and expected_type != inspect._empty:
            try:
                # Cast the parameter value to the expected type
                casted_params[param_name] = expected_type(params[param_name])
            except (ValueError, TypeError) as e:
                raise TypeError(f"Cannot cast {param_name} to {expected_type}: {e}")
        else:
            # If no annotation or the parameter isn't passed, just pass the original
            original_value = params.get(param_name)
            # Only include the parameter if it was passed
            if original_value is not None:
                casted_params[param_name] = original_value

    # Call the function with casted parameters
    return func(**casted_params)

def generate_function_definition_from_callable(function: Callable) -> Dict:
    """Generate a function definition from a callable.
    
    :param function: The callable to generate a function definition for.
    :type function: Callable
    :return: A function definition in the OpenAI Function schema.
    """
    # Map python types to JSON Schema types
    type_map = {
        str: "string",
        int: "integer",
        float: "number",
        bool: "boolean",
        list: "array",
        dict: "object",
        type(None): "null",
    }
    # Parse the function's docstring
    try:
        docstring = parse(function.__doc__)
    except Exception as e:
        raise ValueError(f"Failed to parse docstring: {e}")
    try:
        # Get function signature
        signature = inspect.signature(function)
    except Exception as e:
        raise ValueError(f"Failed to get function signature: {e}")
    # Get function name and signature
    function_name = function.__name__
    # Prepare the function definition
    function_definition = {
        "name": function_name,
        "description": docstring.short_description if docstring.short_description else "",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False
        }
    }
    
    # Parse parameters from the signature and docstring
    for param_name, param in signature.parameters.items():
        param_type = type_map.get(param.annotation, None)
        param_description = ""
        
        # Find the corresponding docstring parameter
        docstring_param = next((p for p in docstring.params if p.arg_name == param_name), None)
        param_description = docstring_param.description if docstring_param else ""
        
        # If no type annotation, use the docstring type name, the worst case scenario, it's a string
        if param_type is None:
            param_type = docstring_param.type_name.lower() if docstring_param.type_name else "string"
    
        function_definition["parameters"]["properties"][param_name] = {
            "type": param_type,
            "description": param_description
        }
        
        # Check if parameter is required
        if param.default == inspect.Parameter.empty:
            function_definition["parameters"]["required"].append(param_name)
    
    return FunctionDefinition(**function_definition)

def dereference_openapi(openapi_doc):
    """Dereferences a Swagger/OpenAPI document by resolving all $ref pointers."""
    try:
        import jsonschema
    except ImportError:
        raise ImportError(
            "The jsonschema library is required to parse OpenAPI documents. "
            "Please install it with `pip install jsonschema`."
        )

    resolver = jsonschema.RefResolver.from_schema(openapi_doc)

    def _dereference(obj):
        if isinstance(obj, dict):
            if "$ref" in obj:
                with resolver.resolving(obj["$ref"]) as resolved:
                    return _dereference(resolved)
            return {k: _dereference(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [_dereference(item) for item in obj]
        else:
            return obj

    return _dereference(openapi_doc)
    
def generate_function_definition_from_openapi_spec(openapi_spec: Dict) -> FunctionDefinition:
    """Generate a function definition from the OpenAPI spec."""
    openapi_spec = dereference_openapi(openapi_spec)
    
    paths = openapi_spec.get("paths", {})
    if not paths:
        raise ValueError("No paths found in the OpenAPI specification.")
    
    # For simplicity, we'll use the first path and method found
    path, path_item = next(iter(paths.items()))
    method, operation = next(iter(path_item.items()))
    
    function_definition = {
        "name": operation.get("operationId", f"{method}_{path}"),
        "description": operation.get("summary", ""),
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
    
    # Handle parameters in the path
    for param in operation.get("parameters", []):
        param_name = param["name"]
        param_schema = param["schema"]
        function_definition["parameters"]["properties"][param_name] = {
            "type": param_schema["type"],
            "description": param.get("description", "")
        }
        if param.get("required", False):
            function_definition["parameters"]["required"].append(param_name)
    
    # Handle request body if present
    if "requestBody" in operation:
        content = operation["requestBody"]["content"]
        if "application/json" in content:
            body_schema = content["application/json"]["schema"]
            if body_schema["type"] == "object":
                for prop_name, prop_schema in body_schema["properties"].items():
                    function_definition["parameters"]["properties"][prop_name] = {
                        "type": prop_schema["type"],
                        "description": prop_schema.get("description", "")
                    }
                    if prop_name in body_schema.get("required", []):
                        function_definition["parameters"]["required"].append(prop_name)
    
    return FunctionDefinition(**function_definition)


def create_base_tool_from_json(json_dict: dict) -> BaseTool:
    """Create a BaseTool instance from a JSON string."""
    name = json_dict["function"]["name"]
    function = FunctionDefinition(
        name=json_dict["function"]["name"],
        description=json_dict["function"]["description"],
        parameters=json_dict["function"]["parameters"]
    )
    
    return BaseTool(name=name, function=function)
            
if __name__ == "__main__":
    output = generate_function_definition_from_callable(generate_function_definition_from_callable)
    print(output)
    openapi_spec = {
        "openapi": "3.0.0",
    "info": {
        "title": "Bland AI Calls API",
        "version": "1.0.0",
        "description": "API for managing calls through Bland AI"
    },
    "servers": [
        {
        "url": "https://api.bland.ai/v1",
        "description": "Production server"
        }
    ],
    "paths": {
        "/calls": {
        "post": {
            "summary": "Create a call task",
            "operationId": "createCallTask",
            "requestBody": {
            "description": "Details of the call task",
            "required": True,
            "content": {
                "application/json": {
                "schema": {
                    "type": "object",
                    "properties": {
                    "phone_number": {
                        "type": "string",
                        "description": "Phone number to call",
                        "example": "+"
                    },
                    "from": {
                        "type": "string",
                        "nullable": True,
                        "description": "Caller name",
                        "example": None
                    },
                    "task": {
                        "type": "string",
                        "description": "Task script for the call",
                        "example": "Your name is Sarah, and you’re a surveyor working on behalf of a small business directory. ..."
                    },
                    "model": {
                        "type": "string",
                        "description": "Model to use for the call",
                        "example": "base"
                    },
                    "language": {
                        "type": "string",
                        "description": "Language of the call",
                        "example": "en"
                    },
                    "voice": {
                        "type": "string",
                        "description": "Voice to use for the call",
                        "example": "maya"
                    },
                    "voice_settings": {
                        "type": "object",
                        "description": "Settings for the voice",
                        "example": {}
                    },
                    "local_dialing": {
                        "type": "boolean",
                        "description": "Enable local dialing",
                        "example": False
                    },
                    "max_duration": {
                        "type": "integer",
                        "description": "Maximum duration of the call in minutes",
                        "example": 12
                    },
                    "answered_by_enabled": {
                        "type": "boolean",
                        "description": "Enable answered by feature",
                        "example": False
                    },
                    "wait_for_greeting": {
                        "type": "boolean",
                        "description": "Wait for greeting before starting the task",
                        "example": False
                    },
                    "record": {
                        "type": "boolean",
                        "description": "Record the call",
                        "example": False
                    },
                    "amd": {
                        "type": "boolean",
                        "description": "Enable answering machine detection",
                        "example": False
                    },
                    "interruption_threshold": {
                        "type": "integer",
                        "description": "Interruption threshold for the call",
                        "example": 100
                    },
                    "voicemail_message": {
                        "type": "string",
                        "nullable": True,
                        "description": "Message to leave on voicemail",
                        "example": None
                    },
                    "temperature": {
                        "type": "number",
                        "nullable": True,
                        "description": "Temperature setting for the call",
                        "example": None
                    },
                    "transfer_list": {
                        "type": "object",
                        "description": "List of transfer options",
                        "example": {}
                    },
                    "metadata": {
                        "type": "object",
                        "description": "Metadata for the call",
                        "example": {}
                    },
                    "pronunciation_guide": {
                        "type": "array",
                        "description": "Pronunciation guide",
                        "items": {
                        "type": "string"
                        },
                        "example": []
                    },
                    "start_time": {
                        "type": "string",
                        "format": "date-time",
                        "nullable": True,
                        "description": "Start time for the call",
                        "example": None
                    },
                    "request_data": {
                        "type": "object",
                        "description": "Additional request data",
                        "example": {}
                    },
                    "tools": {
                        "type": "array",
                        "description": "Tools to use for the call",
                        "items": {
                        "type": "object"
                        },
                        "example": []
                    },
                    "webhook": {
                        "type": "string",
                        "nullable": True,
                        "description": "Webhook URL for call updates",
                        "example": None
                    },
                    "calendly": {
                        "type": "object",
                        "description": "Calendly integration details",
                        "example": {}
                    }
                    },
                    "required": ["phone_number", "task", "model", "language", "voice"]
                }
                }
            }
            },
            "responses": {
            "200": {
                "description": "Call task created successfully",
                "content": {
                "application/json": {
                    "schema": {
                    "type": "object",
                    "properties": {
                        "success": {
                        "type": "boolean",
                        "description": "Indicates if the operation was successful",
                        "example": True
                        },
                        "message": {
                        "type": "string",
                        "description": "Detailed message of the operation",
                        "example": "Call task created successfully"
                        }
                    }
                    }
                }
                }
            },
            "400": {
                "description": "Bad request",
                "content": {
                "application/json": {
                    "schema": {
                    "type": "object",
                    "properties": {
                        "error": {
                        "type": "string",
                        "description": "Error message",
                        "example": "Invalid input data"
                        }
                    }
                    }
                }
                }
            },
            "500": {
                "description": "Internal server error",
                "content": {
                "application/json": {
                    "schema": {
                    "type": "object",
                    "properties": {
                        "error": {
                        "type": "string",
                        "description": "Error message",
                        "example": "Internal server error"
                        }
                    }
                    }
                }
                }
            }
            }
        }
        }
    },
    "components": {
        "schemas": {}
    }
    }
    
    print(generate_function_definition_from_openapi_spec(openapi_spec))