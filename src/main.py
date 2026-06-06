import psycopg2
import os 
from dotenv import load_dotenv    
import json
import requests


load_dotenv()

DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_DATABASE = os.getenv('DB_DATABASE')
DB_PORT = os.getenv('DB_PORT')

def get_db_connection():
    return psycopg2.connect(
        database=DB_DATABASE,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )

def get_locations(cursor): 
    cursor.execute(SELECT location_id,city, lat, long from locations)

try:# set up the api client with cache and retry on error



    locations = cursor.fetchall()

    for location in locations:
        location_id= location[0]
        city = location[1]
        lat = location[2]
        long = location[3]

        print(f"Collecting weather data for {city} (lat: {lat}, long: {long})")

        #collect weather variables 
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": long,
            "daily": ["temperature_2m_max", "temperature_2m_min", "precipitation_sum", "wind_speed_10m_max", ],
            "temperature_unit": "fahrenheit",
        }
        # responses = openmeteo.weather_api(url, params = params)
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        folder_path = '../data/bronze/bronze.json'
        os.makedirs(os.path.dirname(folder_path), exist_ok=True)

        file_path = f"../data/bronze/weather_{location_id}_{city}.json"
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w',encoding="utf-8") as f:
            json.dump(data, f, indent=4)

        

except Exception as e:
    
    print(f"ERROR IN PROCESS", e)
    



