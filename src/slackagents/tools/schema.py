from typing import TypedDict, Dict, Optional, Required, TypeAlias
from enum import Enum
from pydantic import Field, BaseModel
from typing_extensions import Literal

FunctionParameters: TypeAlias = Dict[str, object]

class FunctionDefinition(TypedDict, total=False):
    """"FunctionDefinition is a class that represents the standard function metadata.
    
    We use this class to unify the function definition across internal and external libraries.
    It is taken from `openai.types.shared_params.function_definition.py`.
    """
    
    name: Required[str]
    """The name of the function to be called.

    Must be a-z, A-Z, 0-9, or contain underscores and dashes, with a maximum length
    of 64.
    """

    description: str
    """
    A description of what the function does, used by the model to choose when and
    how to call the function.
    """

    parameters: FunctionParameters
    """The parameters the functions accepts, described as a JSON Schema object.

    See the [guide](https://platform.openai.com/docs/guides/function-calling) for
    examples, and the
    [JSON Schema reference](https://json-schema.org/understanding-json-schema/) for
    documentation about the format.

    Omitting `parameters` defines a function with an empty parameter list.
    """

    strict: Optional[bool]
    """Whether to enable strict schema adherence when generating the function call.

    If set to true, the model will follow the exact schema defined in the
    `parameters` field. Only a subset of JSON Schema is supported when `strict` is
    `true`. Learn more about Structured Outputs in the
    [function calling guide](docs/guides/function-calling).
    """

class AuthType(Enum):
    """AuthType is a class that represents the authentication types."""
    NO_AUTH = "no_auth"
    API_KEY = "api_key"
    BEARER_TOKEN = "bearer_token"
    BASIC_AUTH = "basic_auth"

class APIKeyParams(BaseModel):
    """APIKeyParams is a class that represents the API key parameters."""
    key_name: str = Field(default="api_key", description="The name of the API key parameter")
    key_value: str = Field(..., description="The value of the API key")
    key_in: Literal["header", "query"] = Field(default="header", description="Where to include the API key")

class BearerTokenParams(BaseModel):
    """BearerTokenParams is a class that represents the bearer token parameters."""
    token: str = Field(..., description="The bearer token")

class BasicAuthParams(BaseModel):
    """BasicAuthParams is a class that represents the basic auth parameters."""
    username: str = Field(..., description="The username for basic auth")
    password: str = Field(..., description="The password for basic auth")
