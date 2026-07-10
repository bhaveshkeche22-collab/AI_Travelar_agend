from dotenv import load_dotenv
import os
from langchain.tools import tool
import requests

load_dotenv()

@tool
def get_flight_info(origin: str, destination: str) -> str:
    """
    Search available flights between two cities.

    Use this tool whenever the user asks about:
    - Flights
    - Airlines
    - Flight timings
    - Flight status
    - Available flights

    Args:
        origin: 3-letter IATA airport code (e.g. 'DEL')
        destination: 3-letter IATA airport code (e.g. 'BOM')
    """
    api_key = os.getenv("AVIATIONSTACK_API_KEY")
    if not api_key:
        return "Error: AVIATIONSTACK_API_KEY is not set."

    url = "http://api.aviationstack.com/v1/flights"
    params = {
        "access_key": api_key,
        "dep_iata": origin.upper(),
        "arr_iata": destination.upper(),
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        return f"Error contacting flight API: {e}"
    except ValueError:
        return "Error: Received invalid response from flight API."

    if "error" in data:
        return f"Error: {data['error'].get('message', 'Unknown API error')}"

    flights = data.get("data", [])
    if not flights:
        return f"No flights found from {origin} to {destination}"

    flight = flights[0]

    try:
        airline = flight["airline"]["name"]
        flight_number = flight["flight"]["iata"]
        departure = flight["departure"]["scheduled"]
        arrival = flight["arrival"]["scheduled"]
        status = flight["flight_status"]
    except (KeyError, TypeError):
        return "Error: Flight data was incomplete."

    return (
        f"Airline: {airline}\n"
        f"Flight: {flight_number}\n"
        f"Departure: {departure}\n"
        f"Arrival: {arrival}\n"
        f"Status: {status}"
    )