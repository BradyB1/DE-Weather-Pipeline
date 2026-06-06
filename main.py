from sqlalchemy import create_engine, text
import psycopg2
import os 
from dotenv import load_dotenv    
import pandas as pd 
import openmeteo_requests
import requests_cache
from retry_requests import retry 


load_dotenv()

DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_DATABASE = os.getenv('DB_DATABASE')
DB_PORT = os.getenv('DB_PORT')

connection = psycopg2.connect(database = DB_DATABASE, user = DB_USER, password = DB_PASSWORD, host = DB_HOST, port = DB_PORT)

cursor = connection.cursor()

#log setup
cursor.execute("""
    INSERT INTO etl_run_log (start_time, status, rows_inserted, rows_updated, error_message)
        VALUES (CURRENT_TIMESTAMP, 'running', 0, 0, NULL)
        RETURNING run_id;
""")
run_id = cursor.fetchone()[0]
connection.commit()



try:# set up the api client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)

    cursor.execute("SELECT location_id, city, lat, long FROM locations")

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
        responses = openmeteo.weather_api(url, params = params)

        response = responses[0]

        daily = response.Daily()

        dates = daily.Time()
        temperature_max = daily.Variables(0).ValuesAsNumpy()
        temperature_min = daily.Variables(1).ValuesAsNumpy()
        precipitation_sum = daily.Variables(2).ValuesAsNumpy()
        wind_speed_max = daily.Variables(3).ValuesAsNumpy()

        rows_inserted = 0
        for i in range(len(temperature_max)):
            cursor.execute("""
                        INSERT INTO weather_daily(
                            location_id,
                            weatherdate, 
                            temperature_max,
                                temperature_min,
                                precipitation_sum,
                                wind_speed_max
                        )
                        VALUES (%s, to_timestamp(%s), %s, %s, %s, %s)
                        ON CONFLICT (location_id, weatherdate) DO NOTHING
                        
                        RETURNING weather_id
                        """, (location_id, 
                                dates + i * 86400,
                                int(temperature_max[i]), 
                                int(temperature_min[i]), 
                                round(float(precipitation_sum[i]),2), 
                                int(wind_speed_max[i]))  
                        

            )
        count_inserts = cursor.fetchone()
        
        if count_inserts is not None:
            rows_inserted += 1

    connection.commit()
    
    cursor.execute("""
    UPDATE etl_run_log
    SET status = 'completed',      
        rows_inserted = %s,
        rows_updated = 0,
        error_message = NULL,
        end_time = CURRENT_TIMESTAMP
    WHERE run_id = %s
    
    """, (rows_inserted, run_id))
    connection.commit()
    
    print("Weather data collection and insertion")


except Exception as e:
    connection.rollback()
    cursor.execute("""
        UPDATE etl_run_log
        SET status = 'failed',
            error_message = %s,
            end_time = CURRENT_TIMESTAMP
        WHERE run_id = %s
    """, (str(e), run_id))
    
    connection.commit()
    
    cursor.execute("""
        select error_message 
        from etl_run_log 
        where run_id = %s
                
                   """, (run_id,))
    error_message = cursor.fetchone()[0]
    
    print(f"ERROR IN PROCESS" , error_message)
    



cursor.execute("SELECT * FROM weather_daily" ) 
response = cursor.fetchall()
# df = pd.DataFrame(response, columns=['id', 'location_id', 'weatherdate', 'temperature_max', 'temperature_min', 'precipitation_sum', 'wind_speed_max'])
# print(df.head())


    
cursor.close()

connection.close()