
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



 select DISTINCT city, state_name, TO_CHAR(weatherdate, 'MM-DD-YYYY') as weatherday, temperature_max, temperature_min, precipitation_sum, wind_speed_max
 	from locations
	 LEFT JOIN weather_daily 
	 	on locations.location_id = weather_daily.location_id
	order by weatherday
 ;
 