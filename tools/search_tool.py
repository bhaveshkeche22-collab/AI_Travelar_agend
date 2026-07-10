from dotenv import load_dotenv
load_dotenv()

from langchain.tools import tool
import requests
import os


@tool
def travel_search(query: str) -> str:
    """
    Search for travel-related information.
    """

    api_key = os.getenv("TAVILY_API_KEY")

    url = "https://api.tavily.com/search"

    payload = {
        "api_key": api_key,
        "query": query,
        "search_depth": "basic",
        "max_results": 3
    }

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()

        data = response.json()

        if not data.get("results"):
            return "No travel information found."

        summary = []

        for item in data["results"]:

            title = item.get("title", "")
            content = item.get("content", "")

            # Limit content length
            if len(content) > 200:
                content = content[:200] + "..."

            summary.append(
                f"• {title}\n{content}"
            )

        return "\n\n".join(summary)

    except Exception as e:
        return f"Search Error: {str(e)}"