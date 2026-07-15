from database.mysql import get_chat_history

def format_memory(limit=10):
    history = get_chat_history()

    if not history:
        return ""

    history = history[::-1]  # oldest -> newest

    memory = []

    for chat in history[-limit:]:
        memory.append(f"User: {chat['user_message']}")
        memory.append(f"Assistant: {chat['ai_response']}")

    return "\n".join(memory)