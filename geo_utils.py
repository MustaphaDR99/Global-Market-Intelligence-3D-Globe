import json
import os
from geopy.geocoders import Nominatim
from geopy.exc import GeopyError

CACHE_FILE = "city_coordinates.json"


def get_coordinates(city_list):
    """
    Retrieves coordinates from local cache.
    If a city is missing, it fetches from Nominatim and updates the cache.
    """
    # Load existing cache
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            cache = json.load(f)
    else:
        cache = {}

    # Initialize geolocator (Nominatim is free and required user_agent)
    geolocator = Nominatim(user_agent="market_pipeline_project")
    updated = False

    for city in city_list:
        if city not in cache:
            # Format chosen (e.g., "New_York" -> "New York")
            search_name = city.replace("_", " ")
            print(f"Geocoding {search_name}...")

            try:
                location = geolocator.geocode(search_name)
                if location:
                    cache[city] = {
                        "lat": location.latitude,
                        "lon": location.longitude
                    }
                    updated = True
                else:
                    print(f"Warning: Location not found for {city}")
            except GeopyError as e:
                print(f"Network error geocoding {city}: {e}")

    # Save back to cache if new data was found
    if updated:
        with open(CACHE_FILE, "w") as f:
            json.dump(cache, f, indent=4)
        print(f"SUCCESS: New coordinates cached to {CACHE_FILE}")

    return cache