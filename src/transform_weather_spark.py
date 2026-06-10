from pyspark.sql import SparkSession
from pyspark.sql import functions as F

import os

print("Current folder:", os.getcwd())
print("File exists:", os.path.exists("../data/bronze/weather_1_frederick.json"))

spark = SparkSession.builder \
    .appName("WeatherTransform") \
    .getOrCreate()

bronze_path = "../data/bronze/weather_1_frederick.json"

df = spark.read.option("multiLine", "true").json(bronze_path)

df.printSchema()
df.show(5, truncate=False)

df_zipped = df.withColumn("zipped_column", F.arrays_zip("daily.time", "daily.temperature_2m_max", "daily.temperature_2m_min",
                                                      "daily.precipitation_sum", "daily.wind_speed_10m_max"  ))

df_zipped.show(truncate=False)

df_exploded = df
df_exploded.show(truncate= False)

df_cleaned = df_exploded.select('location_id','city',  F.col("exploded.time").alias("weatherdate"),
    F.col("exploded.temperature_2m_max").alias("temperature_max"),
    F.col("exploded.temperature_2m_min").alias("temperature_min"),
    F.col("exploded.precipitation_sum").alias("precipitation_sum"),
    F.col("exploded.wind_speed_10m_max").alias("wind_speed_max"))


df_cleaned.show(truncate=False)
df_cleaned.printSchema()

spark.stop()