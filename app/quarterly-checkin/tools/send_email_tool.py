def send_email_tool(employee_id: str, subject: str, body: str):
    """Send an email to an employee

    :param employee_id: The employee ID
    :type employee_id: string
    :param subject: The subject of the email
    :type subject: string
    :param body: The body of the email
    :type body: string
    """
    return f"Successfully sent an email to {employee_id} with subject {subject} and body {body}"