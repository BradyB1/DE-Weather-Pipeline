import os
import json
import requests
import psycopg2
from dotenv import load_dotenv


load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_DATABASE = os.getenv("DB_DATABASE")
DB_PORT = os.getenv("DB_PORT")

BRONZE_FOLDER = "../data/bronze"


def get_db_connection():
    return psycopg2.connect(
        database=DB_DATABASE,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )


def get_locations(cursor):
    cursor.execute("SELECT location_id, city, lat, long FROM locations")
    return cursor.fetchall()


def fetch_weather(lat, long):
    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": lat,
        "longitude": long,
        "daily": [
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_sum",
            "wind_speed_10m_max"
        ],
        "temperature_unit": "fahrenheit",
    }

    response = requests.get(url, params=params)
    response.raise_for_status()

    return response.json()


def save_raw_weather(data, location_id, city):
    os.makedirs(BRONZE_FOLDER, exist_ok=True)

    data["location_id"] = location_id
    data["city"] = city

    safe_city = city.replace(" ", "_").lower()
    file_path = f"{BRONZE_FOLDER}/weather_{location_id}_{safe_city}.json"
    
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    return file_path


def main():
    connection = get_db_connection()
    cursor = connection.cursor()
    
    try:
        locations = get_locations(cursor)

        for location in locations:
            location_id = location[0]
            city = location[1]
            lat = location[2]
            long = location[3]

            print(f"Collecting weather data for {city}")

            weather_data = fetch_weather(lat, long)
            file_path = save_raw_weather(weather_data, location_id, city)

            print(f"Saved raw file: {file_path}")

    except Exception as e:
        print("ERROR IN PROCESS:", e)

    finally:
        cursor.close()
        connection.close()


if __name__ == "__main__":
    main()