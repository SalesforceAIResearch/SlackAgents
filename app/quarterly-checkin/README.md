# Quarterly Check-in Workflow

An automated workflow system designed to streamline the employee quarterly check-in process using AI agents and Slack integration.

## Overview

This project implements an automated workflow for managing employee quarterly check-ins, featuring:

- Automated report generation from Jira performance data
- Smart calendar scheduling for check-in meetings
- Automated email notifications
- Slack integration for workflow management

## System Architecture

The system consists of three main AI agents:

1. **Data Agent**
   - Loads employee Jira performance records
   - Generates quarterly check-in reports
   - Manages report revisions and storage

2. **Calendar Agent**
   - Analyzes employee calendars
   - Identifies optimal meeting slots
   - Schedules check-in meetings

3. **Email Agent**
   - Handles automated email communications
   - Sends meeting confirmations and follow-ups

## Installation

1. Clone the repository
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```
## Configuration

1. Create a `.env` file with the following variables:

   ```bash
   CONFIG_PATH=path/to/config.yaml
   ```

2. Configure the Slack integration in `config.yaml`:

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

## Project Structure

```plaintext
app/quarterly-checkin/
├── app.py # Main application entry point
├── config.yaml # Configuration file
├── requirements.txt # Project dependencies
├── README.md # Project documentation
├── assets/ # Storage for employee data
│ ├── calendars/
│ └── reports/
├── prompts/ # AI agent prompt templates
│ ├── data_agent.md
│ ├── calendar_agent.md
│ └── email_agent.md
└── tools/ # Utility functions
├── init.py
├── load_employee_calendar_tool.py
├── load_jira_record_tool.py
├── send_calendar_invite_tool.py
├── send_email_tool.py
└── write_to_markdown_file.py
```

# Features

### Report Generation
- Automated generation of quarterly check-in reports
- Integration with Jira performance management records
- Customizable report templates

### Calendar Management
- Smart scheduling algorithm
- Conflict detection
- Automated calendar invites

### Email Automation
- Automated notification system
- Customizable email templates
- Meeting confirmation and follow-up emails

## Tools

The system includes several utility tools:

- `load_jira_record_tool`: Retrieves employee performance data from Jira
- `load_employee_calendar_tool`: Fetches employee calendar data
- `send_calendar_invite_tool`: Manages calendar invitations
- `send_email_tool`: Handles email communications
- `write_tool`: Manages file operations for reports
