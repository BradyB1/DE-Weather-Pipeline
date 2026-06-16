# 1. Read the Silver Parquet file
# 2. Convert it to rows
# 3. Connect to PostgreSQL
# 4. Insert/upsert into weather_daily
# 5. Count inserted rows
# 6. Log success/failure

    # pandas reads Parquet
    # psycopg2 loads PostgreSQL
    
import pandas as pd 
import duckdb
from extract_weather import get_db_connection
from dotenv import load_dotenv
import os
import requests

load_dotenv()
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_DATABASE = os.getenv("DB_DATABASE")
DB_PORT = os.getenv("DB_PORT")


# print(df.head())
# print(df.info())
# print(df.shape)
# print(df.columns)



show_all = duckdb.sql(
    """ 
        SELECT * 
         FROM '../data/silver/weather_daily/*.parquet'

    """
    
)


listed_cities = duckdb.sql(
    """ 
        SELECT distinct city as active_cities

         FROM '../data/silver/weather_daily/*.parquet'

    """
    
)


print(show_all)
print(listed_cities)




def run_load():
    connection = get_db_connection()
    cursor = connection.cursor()
    
    df = pd.read_parquet("../data/silver/weather_daily")

    rows_inserted = 0

    for _, row in df.iterrows():
        cursor.execute(
            """
                INSERT INTO weather_daily (
                    location_id, 
                    weatherdate,
                    temperature_max,
                    temperature_min,
                    precipitation_sum,
                    wind_speed_max
                )
                VALUES(%s, %s, %s, %s, %s, %s)
                ON CONFLICT (location_id, weatherdate) DO NOTHING
                RETURNING weather_id
            """,(
                int(row["location_id"]),
                row["weatherdate"],
                float(row["temperature_max"]),
                float(row["temperature_min"]),
                float(row["precipitation_sum"]),
                float(row["wind_speed_max"])
            )
        )
        
        inserted_row = cursor.fetchone()
        
        if inserted_row is not None: 
            rows_inserted += 1
            
    connection.commit()
    
    print(f"rows inserted: {rows_inserted}")
    cursor.close()
    connection.close()
    

if __name__ == "__main__":
    run_load()
