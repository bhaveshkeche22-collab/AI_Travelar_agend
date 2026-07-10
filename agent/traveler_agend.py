from dotenv import load_dotenv
load_dotenv()

import os
from langchain_mistralai import ChatMistralAI
from langchain_classic.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate

from tools.flight_tool import get_flight_info
from tools.hotel_tool import hotel_search
from tools.search_tool import travel_search
from tools.weather_tool import get_weather
from tools.budget_tool import estimate_travel_budget

from memory.memory import format_memory
from database.mysql import save_chat_history

from rich import print


# -------------------------------
# LLM
# -------------------------------
llm = ChatMistralAI(
    api_key=os.getenv("MISTRAL_API_KEY"),
    model="mistral-small-2506",
    temperature=0,
)

# -------------------------------
# Tools
# -------------------------------
tools = [
    get_flight_info,
    hotel_search,
    travel_search,
    get_weather,
    estimate_travel_budget
]

# -------------------------------
# Prompt
# -------------------------------
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are an intelligent AI Travel Agent.

You help users with:

- Flight booking
- Hotel recommendations
- Weather information
- Travel budget estimation
- Tourist attractions

Use the available tools whenever necessary.

Always provide clear, structured, and user-friendly answers.
"""
        ),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}")
    ]
)

# -------------------------------
# Create Agent
# -------------------------------
agent = create_tool_calling_agent(
    llm,
    tools,
    prompt
)

travel_agent = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True
)

# -------------------------------
# Main Function
# -------------------------------
def ask_travel_agent(user_query: str):

    memory = format_memory()

    query = f"""
Previous Conversation:

{memory}

Current User Question:

{user_query}
"""

    response = travel_agent.invoke(
        {
            "input": query
        }
    )

    save_chat_history(
        user_query,
        response["output"]
    )

    return response


