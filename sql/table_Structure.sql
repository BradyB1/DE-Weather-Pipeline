-- Database: weather_etl

DROP DATABASE IF EXISTS weather_etl;

CREATE DATABASE weather_etl
   WITH
   OWNER = postgres
   ENCODING = 'UTF8'
   LC_COLLATE = 'English_United States.1252'
   LC_CTYPE = 'English_United States.1252'
   LOCALE_PROVIDER = 'libc'
   TABLESPACE = pg_default
   CONNECTION LIMIT = -1
   IS_TEMPLATE = False;


CREATE TABLE IF NOT EXISTS locations (
    location_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    city VARCHAR(50) NOT NULL,
    state_name VARCHAR(50) NOT NULL,
    country VARCHAR(50) NOT NULL,
    lat DOUBLE PRECISION NOT NULL,
    long DOUBLE PRECISION NOT NULL
);


CREATE TABLE IF NOT EXISTS weather_daily (
	weather_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
	location_id INT NOT NULL,
	weatherdate TIMESTAMP NOT NULL,
	temperature_max INT NOT NULL,
	temperature_min INT NOT NULL,
	precipitation_sum DOUBLE PRECISION NOT NULL,
	wind_speed_max INT NOT NULL,
	created_at TIMESTAMP DEFAULT NOW(),

	CONSTRAINT fk_location
		FOREIGN KEY (location_id) 
		REFERENCES locations(location_id),

	CONSTRAINT unique_location_weatherdate
		UNIQUE(location_id, weatherdate)

);


