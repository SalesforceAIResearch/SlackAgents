"""Default prompt for transition function."""

TRANSITION_FUNCTION_TEMPLATE = """\
{{
    "type": "function",
    "function": {{
        "name": "transition",
        "description": "Initiates a transition to another module. Available transitions are as follows: {transitions}. It is crucial to obtain user approval before executing the transition. After the transition, the user should be informed about the change.",
        "parameters": {{
            "type": "object",
            "properties": {{
                "next_module": {{
                    "type": "string",
                    "description": "The name of the next module to execute."
                }},
                "summary": {{
                    "type": "string",
                    "description": "A summarization of the agent conversations, task executions, etc. before transition."
                }},
                "reason": {{
                    "type": "string",
                    "description": "The reason for transitions."
                }}
            }},
            "required": [
                "next_module",
                "summary",
                "reason"
            ],
            "additionalProperties": false
        }}
    }}
}}
"""