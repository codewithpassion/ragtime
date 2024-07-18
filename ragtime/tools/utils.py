def get_last_user_message(data):
    user_messages = [msg for msg in data.get("messages", []) if msg.get("role") == "user" or msg.get("role") == "human"]
    return user_messages[-1]["content"] if user_messages else None
