# Define the tools for the agent
def load_jira_record_tool(employee_id: str):
    """Load an employee's Jira performance management record
    
    :param employee_id: The employee ID
    :type employee_id: string
    :return: The employee's Jira performance management record
    :rtype: string
    """
    try:
        with open(f"assets/employee_jira_{employee_id}.md", "r") as f:
            return f.read()
    except FileNotFoundError:
        return "Jira record not found"