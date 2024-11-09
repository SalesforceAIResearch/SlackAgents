from typing import Optional

from pydantic import BaseModel, Field, field_validator


class LLMConfig(BaseModel):
    provider: str = Field(
        description="Provider of the LLM (e.g., 'ollama', 'openai')", default="openai"
    )
    # TODO: add provider specific configs. Now we only support openai
    config: Optional[dict] = Field(
        description="Configuration for the specific LLM", default={}
    )

    @field_validator("config")
    def validate_config(cls, v, values):
        provider = values.data.get("provider")
        if provider in (
            "openai",
            "ollama",
            "groq",
            "together",
            "aws_bedrock",
            "litellm",
            "azure_openai",
        ):
            return v
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")