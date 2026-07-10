from dotenv import load_dotenv
import os

import requests
load_dotenv()
from langchain.tools import tool
from rich import print
@tool
def get_weather(city:str)->str:
    """"
    Get the current weather of a city
    """
    api_key = os.getenv("OPENWEATHER_API_KEY")
    url=f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    response=requests.get(url)
    data=response.json()
    if str(data.get("cod")) != "200":
        return f"error:{data.get('message','could not fetch weather data')}"
    temp=data["main"]["temp"]
    desc=data["weather"][0]["description"]
    return f"the current weather of{city} is {temp} °C with {desc}"

