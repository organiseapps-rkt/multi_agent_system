import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("AVIATION_API_KEY")

def search_flights(user_query: str):
    url = "https://api.aviationstack.com/v1/flights"
    params = {
        "api_key": API_KEY,
        "limit": 5
    }
    response = requests.get(url, params=params)
    data = response.json()

    flights = []

    if "data" in data:
        for flight in data["data"][:5]:  # Limit to 5 flights
            flight_info = {
                "flight_number": flight.get("flight", {}).get("iata"),
                "airline": flight.get("airline", {}).get("name"),
                "departure_airport": flight.get("departure", {}).get("airport"),
                "arrival_airport": flight.get("arrival", {}).get("airport"),
                "departure_time": flight.get("departure", {}).get("estimated"),
                "arrival_time": flight.get("arrival", {}).get("estimated"),
                "status": flight.get("flight_status")
            }
            flights.append(flight_info)