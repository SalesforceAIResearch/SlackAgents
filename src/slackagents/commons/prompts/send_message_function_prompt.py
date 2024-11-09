SEND_MESSAGE_FUNCTION_TEMPLATE = """\
{{
    "type": "function",
    "function": {{
        "name": "send_message",
        "description": "Send a message to one of your colleagues or to the message sender.",
        "parameters": {{
            "type": "object",
            "properties": {{
                "content": {{
                    "type": "string",
                    "description": "The content of the message to be sent."
                }},
                "to_whom": {{
                    "type": "string",
                    "description": "The name of the recipient."
                }}
            }},
            "required": [
                "content",
                "to_whom"
            ],
            "additionalProperties": false
        }}
    }}
}}
"""