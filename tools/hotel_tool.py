from dotenv import load_dotenv
load_dotenv()

from langchain.tools import tool
import requests
import os
import json


@tool
def hotel_search(location: str, check_in: str, check_out: str) -> str:
    """
    Search hotels near a location using Geoapify.
    Note:
    Geoapify does NOT support hotel availability or pricing.
    check_in and check_out are accepted only for compatibility.

    Args:
        location: City or place name (e.g. 'Mumbai')
        check_in: Check-in date (accepted but not used)
        check_out: Check-out date (accepted but not used)
    """
    api_key = os.getenv("HOTEL_API_KEY")
    if not api_key:
        return json.dumps({"error": "HOTEL_API_KEY is not set."})

    # Step 1: Convert location to latitude & longitude
    geocode_url = "https://api.geoapify.com/v1/geocode/search"
    geo_params = {"text": location, "apiKey": api_key}

    try:
        geo_response = requests.get(geocode_url, params=geo_params, timeout=10)
        geo_response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return json.dumps({"error": f"Geocoding error: {e}"})

    geo_data = geo_response.json()

    if not geo_data.get("features"):
        return json.dumps({"error": f"Location '{location}' not found."})

    lon, lat = geo_data["features"][0]["geometry"]["coordinates"]

    # Step 2: Search nearby hotels
    places_url = "https://api.geoapify.com/v2/places"
    places_params = {
        "categories": "accommodation.hotel",
        "filter": f"circle:{lon},{lat},50000",
        "limit": 10,
        "apiKey": api_key,
    }

    try:
        response = requests.get(places_url, params=places_params, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return json.dumps({"error": f"Hotel search error: {e}"})

    data = response.json()

    if not data.get("features"):
        return json.dumps({"error": f"No hotels found near {location}."})

    hotels = []
    for hotel in data["features"]:
        prop = hotel.get("properties", {})
        name = prop.get("name")
        if not name:
            continue  # skip unnamed entries, they add noise
        hotels.append({
            "name": name,
            "address": prop.get("formatted", "N/A"),
            "city": prop.get("city", ""),
            "country": prop.get("country", ""),
        })

    if not hotels:
        return json.dumps({"error": f"No named hotels found near {location}."})

    return json.dumps({"hotels": hotels, "note": "Prices and availability are not supported by this API."})