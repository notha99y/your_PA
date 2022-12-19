"""
Script to curl for nea weather api
"""
import math
import urllib.request

import requests


def get_distance(lat1, lat2, lon1, lon2):
    lon1 = math.radians(lon1)
    lon2 = math.radians(lon2)
    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)

    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    )

    c = 2 * math.asin(math.sqrt(a))

    # Radius of earth in kilometers. Use 3956 for miles
    r = 6371
    return c * r


def get_ip():
    response = requests.get("https://api64.ipify.org?format=json").json()
    return response["ip"]


def get_location():
    ip_address = get_ip()
    with urllib.request.urlopen(
        f"https://geolocation-db.com/jsonp/{ip_address}"
    ) as url:
        data = url.read().decode()
        location_info = data.split("(")[1].strip(")")

    location_info = location_info.replace("null", "None")
    return eval(location_info)


def get_weather(location):
    current_lat = location["latitude"]
    current_long = location["longitude"]

    forcast_api_url = (
        "https://api.data.gov.sg/v1/environment/2-hour-weather-forecast"
    )
    air_temp_api_url = "https://api.data.gov.sg/v1/environment/air-temperature"
    forcast_response = requests.get(forcast_api_url).json()
    air_temp_response = requests.get(air_temp_api_url).json()

    area_metadata = forcast_response["area_metadata"]
    closest_distance = 100  # km

    for a in area_metadata:
        distance = get_distance(
            current_lat,
            a["label_location"]["latitude"],
            current_long,
            a["label_location"]["longitude"],
        )
        if distance < closest_distance:
            closest_distance = distance
            closest_location = a["name"]

    for a in forcast_response["items"][0]["forecasts"]:
        if a["area"] == closest_location:
            forecast = a["forecast"]

    total_temp = 0
    for a in air_temp_response["items"][0]["readings"]:
        total_temp += a["value"]
    average_temp = total_temp / len(air_temp_response["items"][0]["readings"])

    weather_info = {
        "info": "2 hour weather forecast in Singapore",
        "location": closest_location,
        "forecast": forecast,
        "temperature": average_temp,
    }

    return weather_info


if __name__ == "__main__":
    location_info = get_location()
    weather_info = get_weather(location_info)
    print(weather_info)
