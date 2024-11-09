GET_THREAD_HISTORY_FUNCTION_TEMPLATE = """\
{{
    "type": "function",
    "function": {{
        "name": "get_thread_history",
        "description": "Get the history of messages in the current thread if you need to know more context for the conversation.",
        "parameters": {{
            "type": "object",
            "properties": {{}},
            "required": [],
            "additionalProperties": false
        }}
    }}
}}
"""