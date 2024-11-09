def send_calendar_invite_tool(employee_id: str, time_slot: str, meeting_title: str, notes: str):
    """Send a calendar invite to multiple employees
    
    :param employee_id: The employee ID
    :type employee_id: string
    :param time_slot: The time slot to send the invite to
    :type time_slot: string
    :param meeting_title: The title of the meeting
    :type meeting_title: string
    :param notes: The notes of the meeting
    :type notes: string
    """
    return f"Successfully scheduled the meeting with {employee_id} at {time_slot} with title {meeting_title} and notes {notes}"