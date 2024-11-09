def load_employee_calendar_tool(employee_id: str):
    """Load an employee's calendar for the quarter
    
    :param employee_id: The employee ID
    :type employee_id: string
    :return: The employee's calendar for the quarter
    :rtype: string
    """
    with open(f"assets/employee_calendar_{employee_id}.md", "r") as f:
        return f.read()