"""Default prompt for restart function."""

RESTART_FUNCTION_TEMPLATE = """\
{
    "type": "function",
    "function": {
        "name": "restart_workflow",
        "description": "Initiates a workflow restart. This function should only be used when the current workflow cannot meet user requests. It is essential to obtain user confirmation before proceeding with the restart.",
        "parameters": {
            "type": "object",
            "properties": {
                "summary": {
                    "type": "string",
                    "description": "A summarization of the agent conversations, task executions, etc. before restart."
                },
                "reason": {
                    "type": "string",
                    "description": "The reason for restarting the workflow."
                }
            },
            "required": [
                "summary",
                "reason"
            ],
            "additionalProperties": false
        }
    }
}
""".strip()