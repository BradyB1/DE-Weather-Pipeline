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

CREATE TABLE etl_run_log (
    run_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    pipeline_name VARCHAR(100),
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    status VARCHAR(20),
    rows_inserted INTEGER,
    rows_updated INTEGER,
    error_message TEXT
);


INSERT INTO locations (city, state_name, country, lat, long)
	VALUES('Frederick', 'Maryland', 'USA', 39.4143, 77.4105);

INSERT INTO locations ( city, state_name, country, lat, long)
	VALUES('Baltimore', 'Maryland', 'USA', 39.2905, 76.6104);

INSERT INTO locations (city, state_name, country, lat, long)
	VALUES('Westminster', 'Maryland', 'USA', 39.5754, 76.9958);

INSERT INTO locations (city, state_name, country, lat, long)
	VALUES('Rockville', 'Maryland', 'USA', 39.0832, 77.1529);

INSERT INTO locations (city, state_name, country, lat, long)
	VALUES('Annapolis ', 'Maryland', 'USA', 38.9764, 76.4896);
	
-- INSERT INTO weather_daily (weather_id, location_id, weatherdate, temperature_max, temperature_min, precipitation_sum, wind_speed_max, created_at)
-- 	VALUES (1, 1, '2026-06-03 14:30:00', 72, 59, .1, 5, NOW());


-- select * from locations;
-- select * from weather_daily;

-- select l.city, l.state_name, w.temperature_max, w.temperature_min  
-- 	from locations l
-- 	LEFT JOIN weather_daily w
-- 		on l.location_id = w.location_id;
		




-- DROP TABLE locations cascade;
-- DROP TABLE weather_daily;
-- DROP TABLE etl_run_log;



 select DISTINCT city, state_name, TO_CHAR(weatherdate, 'MM-DD-YYYY') as weatherday, temperature_max, temperature_min, precipitation_sum, wind_speed_max
 	from locations
	 LEFT JOIN weather_daily 
	 	on locations.location_id = weather_daily.location_id
	order by weatherday
 ;
 