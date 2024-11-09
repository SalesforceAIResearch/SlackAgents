import re

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
WORKING_EMOJI = "eyes"
SOLVING_EMOJI = "completed"


def convert_markdown_to_slack(text):
    # Convert links: [text](url) to <url|text>
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"<\2|\1>", text)

    # Convert bold: **text** or __text__ to *text*
    text = re.sub(r"\*\*([^\*]+)\*\*|__([^_]+)__", r"*\1\2*", text)

    # Convert italic: *text* or _text_ to _text_
    # Note: Slack uses _ for italic, which overlaps with Markdown's usage.
    # This simple replacement may conflict with bold syntax in complex cases.
    # text = re.sub(r"\*([^\*]+)\*|_([^_]+)_", r"_\1\2_", text)

    # Convert inline code: `code` to `code`
    # Slack's inline code syntax is the same as Markdown's, so no change is needed.

    # Add additional conversions as needed here

    return text


def block_message(message: str) -> dict:
    """Block message for slack

    :param message: message to be blocked
    :type message: str
    :return: blocked message
    :rtype: dict
    """
    message = convert_markdown_to_slack(message)
    print(message)
    return {
        "type": "section",
        "text": {"type": "mrkdwn", "text": message},
    }

def get_mention_ids(text: str) -> list:
    return re.findall(r"<@(\w+)>", text)

def remove_mentions(text):
    return re.sub(r"<@(\w+)>", "", text)

def get_bot_user_id(bot_token: str) -> str:
    """
    Get the bot user ID using the Slack API.
    Returns:
        str: The bot user ID.
    """
    try:
        # Initialize the Slack client with your bot token
        slack_client = WebClient(
            token=bot_token
        )
        response = slack_client.auth_test()
        return response["user_id"]
    except SlackApiError as e:
        raise e
    
def get_channel_user_ids_and_names(channel_id: str, bot_token: str) -> dict:
    """
    Get all user IDs and names in a Slack channel.
    
    Args:
        channel_id (str): The Slack channel ID.
        bot_token (str): The bot token for authentication.
        
    Returns:
        dict: A dictionary with user IDs as keys and user names as values.
    """
    slack_client = WebClient(token=bot_token)
    user_ids = []
    user_id_name_map = {}
    next_cursor = None

    while True:
        try:
            # Call the Slack API to get members of the channel
            result = slack_client.conversations_members(channel=channel_id, cursor=next_cursor)
            user_ids.extend(result["members"])
            next_cursor = result["response_metadata"].get("next_cursor")
            if not next_cursor:
                break
        except SlackApiError as e:
            raise e

    for user_id in user_ids:
        try:
            user_info = slack_client.users_info(user=user_id)
            # print(f"user_info: {user_info}")
            user_name = user_info["user"]["real_name"]
            user_id_name_map[user_id] = user_name
        except SlackApiError as e:
            raise e

    return user_id_name_map

def strip_user_mention_from_message(message: str, user_id: str) -> str:
    return re.sub(f"<@{user_id}>", "", message)


def get_thread_history(
    channel_id: str, 
    thread_ts: str, 
    bot_token: str,
    latest_ts: str = None,
    oldest: str = None,
) -> list:
    """
    Get the message history of a specific thread in a Slack channel.
    
    Args:
        channel_id (str): The Slack channel ID
        thread_ts (str): The timestamp of the parent message that started the thread
        bot_token (str): The bot token for authentication
        
    Returns:
        list: A list of messages in the thread
    """
    # get the parent message ts if the thread_ts is not the parent message ts
    slack_client = WebClient(token=bot_token)
    result = slack_client.conversations_replies(channel=channel_id, ts=thread_ts)
    parent_ts = result["messages"][0]["thread_ts"]
    print(f"parent_ts: {parent_ts}")
    latest_ts = latest_ts if latest_ts is not None else thread_ts
    
    messages = []
    
    try:
        # Call the Slack API to get all the messages in the thread
        result = slack_client.conversations_replies(
            channel=channel_id,
            ts=parent_ts,
            latest=latest_ts,
            oldest=oldest
        )
        messages = result["messages"]
        return messages
        
    except SlackApiError as e:
        raise e

def format_thread_history_to_conversation(
    thread_history: list,
    thread_ts: str,
    user_id_name_map: dict,
    viewer_user_id: str
) -> str:
    """
    Convert Slack thread history into a formatted conversation history.

    Args:
        thread_history (list): List of messages in the thread.
        thread_ts (str): The timestamp of the thread to filter messages.
        user_id_name_map (dict): A dictionary mapping user IDs to user names.

    Returns:
        str: Formatted conversation history.
    """
    conversation_history = []

    for message in thread_history:
        # Skip messages that are at or after the thread timestamp
        if message['ts'] >= thread_ts:
            continue

        # Get the sender's name
        user_id = message.get('user')
        if user_id == viewer_user_id:
            sender_name = "yourself"
        else:
            sender_name = user_id_name_map.get(user_id, "Unknown")

        # Replace user mentions with their names or if it is the viewer, replace it as you
        text = message['text']
        for mentioned_user_id in re.findall(r"<@(\w+)>", text):
            if mentioned_user_id == viewer_user_id:
                mentioned_name = "you"
            else:
                mentioned_name = user_id_name_map.get(mentioned_user_id, "Unknown")
            text = text.replace(f"<@{mentioned_user_id}>", f"<Mentioned>{mentioned_name}</Mentioned>")

        # Format the message. If the sender is the viewer, format it as you.
        
        formatted_message = f"[Message from {sender_name}] {text}"
        conversation_history.append(formatted_message)

    return "\n".join(conversation_history)

def delete_message(channel_id: str, message_ts: str, bot_token: str):
    slack_client = WebClient(token=bot_token)
    try:
        slack_client.chat_delete(channel=channel_id, ts=message_ts)
    except SlackApiError as e:
        if e.response['error'] == 'cant_delete_message':
            print(f"Cannot delete message with timestamp {message_ts} in channel {channel_id}.")
        else:
            raise e

def delete_thread(channel_id: str, thread_ts: str, bot_token: str):
    messages = get_thread_history(channel_id, thread_ts, bot_token)
    for message in messages:
        # Check if the bot is the author of the message
        print(f"message: {message}")
        if message.get('user') == get_bot_user_id(bot_token):
            delete_message(channel_id, message['ts'], bot_token)
        else:
            print(f"Skipping message {message['ts']} as it was not sent by the bot.")

def delete_channel_history(channel_id: str, bot_token: str):
    slack_client = WebClient(token=bot_token)
    messages = slack_client.conversations_history(channel=channel_id)  # This will return a list of messages in the channel
    bot_id = get_bot_user_id(bot_token)
    for message in messages['messages']:
        # Only delete messages sent by the bot
        print(f"message: {message}")
        if message.get('user') == bot_id:
            delete_message(channel_id, message['ts'], bot_token)
        else:
            print(f"Skipping message {message['ts']} as it was not sent by the bot.")
