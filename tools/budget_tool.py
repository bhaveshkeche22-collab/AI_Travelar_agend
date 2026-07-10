from dotenv import load_dotenv
load_dotenv()

from langchain.tools import tool
import google.generativeai as genai
import os


model = genai.GenerativeModel("gemini-2.5-flash")


@tool
def estimate_travel_budget(
    destination: str,
    days: int,
    travelers: int,
    budget_type: str
) -> str:
    """
    Estimate the total travel budget for a trip.
    """
    api_key = "AQ.Ab8RN6KUi5cxeyI2d80eZriYzK9peF7YhH3tkkstKBW2uFXqZg"

    prompt = f"""
    Estimate the travel budget for the following trip.

    Destination: {destination}
    Number of Days: {days}
    Number of Travelers: {travelers}
    Budget Type: {budget_type}

    Include:
    - Flight
    - Hotel
    - Food
    - Local Transport
    - Activities
    - Total Estimated Cost

    Present the answer in a clean, readable format.
    """

    response = model.generate_content(prompt)

    return response.text

