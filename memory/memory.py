from database.mysql import get_chat_history


def load_memory(limit=5):
    """
    Load the last few conversations from the database.
    """

    history = get_chat_history()

    memory = []

    for chat in history[:limit]:
        memory.append(
            {
                "user": chat["user_message"],
                "assistant": chat["ai_response"]
            }
        )

    return memory


def format_memory(limit=5):
    """
    Convert chat history into a prompt for the LLM.
    """

    history = load_memory(limit)

    conversation = ""

    for chat in history:
        conversation += f"User: {chat['user']}\n"
        conversation += f"Assistant: {chat['assistant']}\n\n"

    return conversation