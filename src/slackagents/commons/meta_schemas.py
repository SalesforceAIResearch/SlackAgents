from pydantic import BaseModel, Field
from slackagents.tools.base import BaseTool
from typing import List, Dict
from openai import OpenAI
from slackagents.commons.prompts.meta_prompts import ASSISTANT_GEN_META_PROMPT, SYSTEM_PROMPT_GEN_META_PROMPT, WORKFLOW_AGENT_GEN_META_PROMPT

import json

client = OpenAI()

class AssistantMetaSchema(BaseModel):
    name: str = Field(description="The name of the assistant")
    desc: str = Field(description="The description of the assistant")
    tools: List[BaseTool] = Field(description="The tools that the assistant can use")
    system_prompt: str = Field(description="The system instruction for the assistant")

class TransitionSchema(BaseModel):
    source: str = Field(description="The source node of the transition")
    target: str = Field(description="The target node of the transition")
    description: str = Field(description="The description of the transition condition")

class WorkflowAgentMetaSchema(BaseModel):
    name: str = Field(description="The name of the workflow agent")
    desc: str = Field(description="The description of the workflow agent")
    nodes: Dict[str, AssistantMetaSchema] = Field(description="The assistant nodes of the workflow agent")
    transitions: List[TransitionSchema] = Field(description="The transitions between the assistant nodes of the workflow agent")
    initial_module: str = Field(description="The initial node name of the workflow agent")

def generate_prompt(task_or_prompt: str):
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT_GEN_META_PROMPT,
            },
            {
                "role": "user",
                "content": "Current Assistant System Prompt with Tools Schema:\n" + task_or_prompt + "You should focus on refining the system prompt to define the assistant's behavior, to include components for role play, control flow, output refinement; facilitate automation; grounding. The system prompt should focus on how to use the tools provided in the tools schema combinatorially as a policy to achieve the task. You should not add any new tools to the tools in the policy.",
            },
        ],
    )
    return completion.choices[0].message.content

def generate_assistant(description: str):
    
    json_schema = {
        "name": "assistant_meta_schema",
        "schema": AssistantMetaSchema.model_json_schema()
    }
    
    completion = client.chat.completions.create(
        model="gpt-4o",
        response_format={"type": "json_schema", "json_schema": json_schema},
        messages=[
            {
                "role": "system",
                "content": ASSISTANT_GEN_META_PROMPT,
            },
            {
                "role": "user",
                "content": "Build an assistant for the following task:\n" + description,
            },
        ],
    )
    # Step 1: Generate an initial assistant schema
    assistant_schema = completion.choices[0].message.content
    system_prompt = generate_prompt(assistant_schema)   
    # Step 2: Refine the assistant system prompt
    assistant_schema = json.loads(assistant_schema)
    assistant_schema["system_prompt"] = system_prompt
    return assistant_schema

def generate_workflow_agent(description: str):
    json_schema = {
        "name": "workflow_agent_meta_schema",
        "schema": WorkflowAgentMetaSchema.model_json_schema()
    }
    completion = client.chat.completions.create(
        model="gpt-4o",
        response_format={"type": "json_schema", "json_schema": json_schema},
        messages=[
            {
                "role": "system",
                "content": WORKFLOW_AGENT_GEN_META_PROMPT,
            },
            {
                "role": "user",
                "content": "Build a workflow agent for the following task:\n" + description,
            },
        ],
    )
    # Step 1: Generate an initial workflow schema
    workflow_schema = completion.choices[0].message.content
    workflow_schema = json.loads(workflow_schema)
    # Step 2: Refine system prompts for each node
    for node in workflow_schema["nodes"]:
        assistant_schema = workflow_schema["nodes"][node]
        system_prompt = generate_prompt(str(assistant_schema))
        assistant_schema["system_prompt"] = system_prompt
    return workflow_schema

if __name__ == "__main__":
    print(generate_assistant("Executive assistant."))
    print(generate_workflow_agent("Onboarding workflow."))
