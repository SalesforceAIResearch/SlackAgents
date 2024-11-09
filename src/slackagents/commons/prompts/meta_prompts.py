SYSTEM_PROMPT_GEN_META_PROMPT = """
Given a task description or existing prompt, produce a detailed system prompt to guide a language model in completing the task effectively.

# Guidelines

- Understand the Task: Grasp the main objective, goals, requirements, constraints, and expected output.
- Minimal Changes: If an existing prompt is provided, improve it only if it's simple. For complex prompts, enhance clarity and add missing elements without altering the original structure.
- Reasoning Before Conclusions**: Encourage reasoning steps before any conclusions are reached. ATTENTION! If the user provides examples where the reasoning happens afterward, REVERSE the order! NEVER START EXAMPLES WITH CONCLUSIONS!
    - Reasoning Order: Call out reasoning portions of the prompt and conclusion parts (specific fields by name). For each, determine the ORDER in which this is done, and whether it needs to be reversed.
    - Conclusion, classifications, or results should ALWAYS appear last.
- Examples: Include high-quality examples if helpful, using placeholders [in brackets] for complex elements.
   - What kinds of examples may need to be included, how many, and whether they are complex enough to benefit from placeholders.
- Clarity and Conciseness: Use clear, specific language. Avoid unnecessary instructions or bland statements.
- Formatting: Use markdown features for readability. DO NOT USE ``` CODE BLOCKS UNLESS SPECIFICALLY REQUESTED.
- Preserve User Content: If the input task or prompt includes extensive guidelines or examples, preserve them entirely, or as closely as possible. If they are vague, consider breaking down into sub-steps. Keep any details, guidelines, examples, variables, or placeholders provided by the user.
- Constants: DO include constants in the prompt, as they are not susceptible to prompt injection. Such as guides, rubrics, and examples.
- Output Format: Explicitly the most appropriate output format, in detail. This should include length and syntax (e.g. short sentence, paragraph, JSON, etc.)
    - For tasks outputting well-defined or structured data (classification, JSON, etc.) bias toward outputting a JSON.
    - JSON should never be wrapped in code blocks (```) unless explicitly requested.

The final prompt you output should adhere to the following structure below. Do not include any additional commentary, only output the completed system prompt. SPECIFICALLY, do not include any additional messages at the start or end of the prompt. (e.g. no "---")

[Concise instruction describing the task - this should be the first line in the prompt, no section header]

[Additional details as needed.]

[Optional sections with headings or bullet points for detailed steps.]

# Steps [optional]

[optional: a detailed breakdown of the steps necessary to accomplish the task]

# Output Format

[Specifically call out how the output should be formatted, be it response length, structure e.g. JSON, markdown, etc]

# Examples [optional]

[Optional: 1-3 well-defined examples with placeholders if necessary. Clearly mark where examples start and end, and what the input and output are. User placeholders as necessary.]
[If the examples are shorter than what a realistic example is expected to be, make a reference with () explaining how real examples should be longer / shorter / different. AND USE PLACEHOLDERS! ]

# Notes [optional]

[optional: edge cases, details, and an area to call or repeat out specific important considerations]
""".strip()

ASSISTANT_GEN_META_PROMPT = """
# Instructions
Return a valid assistant formatted in the described JSON schema.

You must also make sure:
- all fields in an object are set as required
- I REPEAT, ALL FIELDS MUST BE MARKED AS REQUIRED
- all objects must have additionalProperties set to false
    - because of this, some cases like "attributes" or "metadata" properties that would normally allow additional properties should instead have a fixed set of properties
- all objects must have properties defined
- field order matters. any form of "thinking" or "explanation" should come before the conclusion
- $defs must be defined under the schema param

Notable keywords NOT supported include:
- For strings: minLength, maxLength, pattern, format
- For numbers: minimum, maximum, multipleOf
- For objects: patternProperties, unevaluatedProperties, propertyNames, minProperties, maxProperties
- For arrays: unevaluatedItems, contains, minContains, maxContains, minItems, maxItems, uniqueItems

Other notes:
- definitions and recursion are supported
- only if necessary to include references e.g. "$defs", it must be inside the "schema" object

# Examples
Input: Generate an assistant that can help brainstorm and write an abstract for a given topic.
Output: {
    "name": "Paper Guru",
    "desc": "An assistant that can help brainstorm an abstract for a given topic",
    "tools": [
        {
            "name": "arxiv_search",
            "function": {
                "name": "arxiv_search",
                "description": "A tool to query arxiv.org.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The query to be passed to arXiv."
                        },
                        "sort_by": {
                            "type": "string",
                            "description": "Either 'relevance' (default) or 'recent'"
                        },
                        "max_results": {
                            "type": "number",
                            "description": "The maximum number of results to return"
                        }
                    },
                    "required": [
                        "query"
                    ],
                    "additionalProperties": false
                }
            }
        },
        {
            "name": "abstract_writer_tool",
            "function": {
                "name": "abstract_writer_tool",
                "description": "A tool to write an academic paper abstract for a given topic",
                "parameters": {
                    "properties": {
                        "topic": {
                            "description": "The topic of the abstract",
                            "title": "Topic",
                            "type": "string"
                        },
                        "context": {
                            "description": "The context of the topic from other sources (e.g, academic papers, etc.)",
                            "title": "Context",
                            "type": "string"
                        }
                    },
                    "required": [
                        "topic",
                        "context"
                    ],
                    "title": "AbstractWriterTool",
                    "type": "object",
                    "additionalProperties": false
                },
                "strict": true
            }
        }
    ],
    "system_prompt": "You are an AI assistant that can help brainstorm an abstract for a given topic."
}
""".strip()

WORKFLOW_AGENT_GEN_META_PROMPT = """
# Instructions
Return a valid workflow agent formatted in the described JSON schema.

You must also make sure:
- all fields in an object are set as required
- I REPEAT, ALL FIELDS MUST BE MARKED AS REQUIRED
- all objects must have additionalProperties set to false
    - because of this, some cases like "attributes" or "metadata" properties that would normally allow additional properties should instead have a fixed set of properties
- all objects must have properties defined
- field order matters. any form of "thinking" or "explanation" should come before the conclusion
- $defs must be defined under the schema param

Notable keywords NOT supported include:
- For strings: minLength, maxLength, pattern, format
- For numbers: minimum, maximum, multipleOf
- For objects: patternProperties, unevaluatedProperties, propertyNames, minProperties, maxProperties
- For arrays: unevaluatedItems, contains, minContains, maxContains, minItems, maxItems, uniqueItems

Other notes:
- definitions and recursion are supported
- only if necessary to include references e.g. "$defs", it must be inside the "schema" object

# Examples
Input: Generate a workflow agent for the task of quarterly check-in.
Output: {
    "name": "Quarterly Check-in Workflow",
    "desc": "Workflow designed to automate the employee quarterly check-in process",
    "nodes": {
        "data_agent": {
            "name": "Data Agent",
            "desc": "Step to load an employee's Jira record and generate a report",
            "tools": [
                {
                    "name": "load_jira_record_tool",
                    "function": {
                        "name": "load_jira_record_tool",
                        "description": "A tool to load an employee's Jira record",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "jira_url": {
                                    "type": "string",
                                    "description": "The URL of the Jira record"
                                }
                            },
                            "required": [
                                "jira_url"
                            ],
                            "additionalProperties": false
                        }
                    }
                }
            "system_prompt": "You are an AI agent designed to help employees summarize the employee's progress against their set goals by generating a report."
        },
        "calendar_agent": {
            "name": "Calendar Agent",
            "desc": "Step to load calendars and send calendar invites",
            "tools": [
                {
                    "name": "load_employee_calendar_tool",
                    "function": {
                        "name": "load_employee_calendar_tool",
                        "description": "A tool to load an employee's calendar",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "calendar_url": {
                                    "type": "string",
                                    "description": "The URL of the calendar"
                                }
                            },
                            "required": [
                                "calendar_url"
                            ],
                            "additionalProperties": false
                        }
                    }
                    }
            ],
            "system_prompt": "You are an AI agent designed to help load an employee's calendar and send calendar invites."
        }
    ],
    "transitions": [
        {
            "source": "Data Agent",
            "target": "Calendar Agent",
            "description": "Transition after report is written"
        }
    ],
    "initial_module": "Data Agent"
}
""".strip()
