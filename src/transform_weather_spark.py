from pyspark.sql import SparkSession
from pyspark.sql import functions as F
import os


BRONZE_PATH = "../data/bronze/*.json"
SILVER_PATH = "../data/silver/weather_daily"


def create_spark_session():
    return SparkSession.builder \
        .appName("WeatherTransform") \
        .getOrCreate()


def read_bronze_weather(spark):
    return spark.read.option("multiLine", "true").json(BRONZE_PATH)


def transform_weather(df):
    df_zipped = df.withColumn(
        "zipped_column",
        F.arrays_zip(
            "daily.time",
            "daily.temperature_2m_max",
            "daily.temperature_2m_min",
            "daily.precipitation_sum",
            "daily.wind_speed_10m_max"
        )
    )

    df_exploded = df_zipped.withColumn(
        "exploded",
        F.explode("zipped_column")
    )

    df_cleaned = df_exploded.select(
        "location_id",
        "city",
        F.col("exploded.time").alias("weatherdate"),
        F.col("exploded.temperature_2m_max").alias("temperature_max"),
        F.col("exploded.temperature_2m_min").alias("temperature_min"),
        F.col("exploded.precipitation_sum").alias("precipitation_sum"),
        F.col("exploded.wind_speed_10m_max").alias("wind_speed_max")
    )

    return df_cleaned


def write_silver_weather(df):
    df.write.mode("overwrite").parquet(SILVER_PATH)


def run_transform():
    spark = create_spark_session()

    try:
        print("Current folder:", os.getcwd())

        df = read_bronze_weather(spark)

        print("Bronze schema:")
        df.printSchema()

        df_cleaned = transform_weather(df)

        print("Cleaned preview:")
        df_cleaned.show(20, truncate=False)

        write_silver_weather(df_cleaned)

        print(f"Silver weather data written to: {SILVER_PATH}")

    finally:
        spark.stop()


if __name__ == "__main__":
    run_transform()