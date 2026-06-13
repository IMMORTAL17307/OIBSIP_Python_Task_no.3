import json
import urllib.request
import urllib.parse
import urllib.error

WMO_WEATHER_CODES = {
    0: "Clear Sky",
    1: "Mainly Clear",
    2: "Partly Cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing Rime Fog",
    51: "Light Drizzle",
    55: "Dense Drizzle",
    56: "Light Freezing Drizzle",
    57: "Dense Freezing Drizzle",
    61: "Slight Rain",
    63: "Moderate Rain",
    65: "Heavy Rain",
    66: "Light Freezing Rain",
    67: "Heavy Freezing Rain",
    71: "Slight Snow Fall",
    73: "Moderate Snow Fall",
    75: "Heavy Snow Fall",
    77: "Snow Grains",
    80: "Slight Rain Showers",
    81: "Moderate Rain Showers",
    82: "Violent Rain Showers",
    85: "Slight Snow Showers",
    86: "Heavy Snow Showers",
    95: "Thunderstorm",
    96: "Thunderstorm with Slight Hail",
    99: "Thunderstorm with Heavy Hail"
}

def get_weather_description(code):
    return WMO_WEATHER_CODES.get(code, "Unknown Conditions")

def fetch_weather(city_name):
    encoded_city = urllib.parse.quote(city_name)
    geocoding_url = f"https://geocoding-api.open-meteo.com/v1/search?name={encoded_city}&count=1&language=en&format=json"
    
    try:
        req = urllib.request.Request(geocoding_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            geo_data = json.loads(response.read().decode())
    except urllib.error.URLError as e:
        print(f"\n[Error] Failed to connect to the geocoding service: {e.reason}")
        return
    except Exception as e:
        print(f"\n[Error] A connection error occurred: {e}")
        return

    results = geo_data.get('results')
    if not results:
        print(f"\n[Error] City '{city_name}' could not be found. Please check spelling.")
        return

    city_info = results[0]
    lat = city_info['latitude']
    lon = city_info['longitude']
    display_name = city_info['name']
    country = city_info.get('country', 'Unknown Country')
    admin1 = city_info.get('admin1', '')

    weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,weather_code"
    
    try:
        req = urllib.request.Request(weather_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            weather_data = json.loads(response.read().decode())
    except urllib.error.URLError as e:
        print(f"\n[Error] Failed to connect to the weather service: {e.reason}")
        return
    except Exception as e:
        print(f"\n[Error] An error occurred while retrieving weather data: {e}")
        return

    current = weather_data.get('current')
    if not current:
        print("\n[Error] Could not parse current weather metrics.")
        return

    temp = current['temperature_2m']
    humidity = current['relative_humidity_2m']
    code = current['weather_code']
    condition = get_weather_description(code)

    location_str = f"{display_name}, {admin1}, {country}" if admin1 else f"{display_name}, {country}"
    print("\n-----------------------------------------")
    print(f"Location:    {location_str}")
    print(f"Coordinates: {lat:.4f}°N, {lon:.4f}°E")
    print(f"Temperature: {temp}°C")
    print(f"Humidity:    {humidity}%")
    print(f"Condition:   {condition}")
    print("-----------------------------------------")

def is_valid_location(location):
    if not location:
        return False, "Error: Location cannot be empty."
    
    allowed_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 -,,.")
    if not all(c in allowed_chars for c in location):
        return False, "Error: Location contains invalid characters. Use only letters, numbers, spaces, commas, or hyphens."
        
    return True, ""

def run_weather_app():
    print("=========================================")
    print("            WEATHER APPLICATION          ")
    print("=========================================")
    
    city_name = input("Enter city name or ZIP/postal code (e.g. New York, 10001): ").strip()
    is_valid, error_msg = is_valid_location(city_name)
    if not is_valid:
        print(error_msg)
        return
        
    print(f"\nFetching weather details for '{city_name}'...")
    fetch_weather(city_name)
    print("=========================================")

if __name__ == "__main__":
    while True:
        run_weather_app()
        print()
        again = input("Do you want to search another location? (yes/no): ").strip().lower()
        if again != "yes" and again != "y":
            print("\nThank you for using the Weather App. Have a wonderful day!")
            break
        print()
