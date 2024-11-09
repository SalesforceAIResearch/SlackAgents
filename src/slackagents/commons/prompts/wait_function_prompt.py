WAIT_FUNCTION_TEMPLATE = """\
{{
    "type": "function",
    "function": {{
        "name": "wait",
        "description": "Wait for the next message.",
        "parameters": {{
            "type": "object",
            "properties": {{
                "reason": {{
                    "type": "string",
                    "description": "The reason for waiting."
                }}
            }},
            "required": [
                "reason"
            ],
            "additionalProperties": false
        }}
    }}
}}
"""