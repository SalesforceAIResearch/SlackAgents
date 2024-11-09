# Code Interpreter

A powerful Slack-based AI assistant that can execute Python code and perform various tasks through code generation and execution.

## Overview

Code Interpreter is a Slack bot that combines natural language understanding with Python code execution capabilities. It can help users accomplish various tasks by generating and executing Python code, accessing the internet, and processing data.

## Features

- **Python Code Execution**: Executes Python code safely in a sandboxed environment
- **Internet Access**: Can perform Google searches and web scraping
- **Data Processing**: Supports libraries like numpy, pandas, matplotlib, and scikit-learn
- **Interactive Workflow**: Human-in-the-loop approach with code review before execution
- **File Management**: Handles file operations and maintains workspace state

## Available Tools

- **Code Interpreter**: Executes Python code and manages file operations
- **Google Search**: Performs web searches using the SerpAPI

## Setup

1. Clone the repository
2. Setup the Python Sandbox for code execution. See [here](https://github.com/airesearch-emu/SlackAgents/tree/clean/sandbox) for more details.
3. Create a `.env` file with the following variables by copying the `.env.example` file:

   ```bash
   SANDBOX_URL=your_sandbox_url
   WORKSPACE_DIR=your_workspace_directory
   SERPAPI_API_KEY=your_serpapi_key
   CONFIG_PATH=path_to_config.yaml
   ```

4. In `config.yaml`, fill in the `slackConfig` section with your Slack App ID, Bot Token, and App Token:

   ```yaml
   id: 
   SLACK_BOT_TOKEN: 
   SLACK_APP_TOKEN: 
   ```
   
If you don't have a Slack App ID, you can create one by following the instructions [here](https://github.com/slack-samples/bolt-python-assistant-template?tab=readme-ov-file).

## Usage

Run the application:

```bash
python app.py
```
