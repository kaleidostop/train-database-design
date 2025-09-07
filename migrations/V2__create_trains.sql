
CREATE TABLE IF NOT EXISTS Trains (
	train_id serial primary key,
	type int references TrainTypes(train_types_id),
    number int,
    total_carriages int,
    total_seats int
);

CREATE TABLE IF NOT EXISTS Stations (
	station_id serial primary key, 
	name varchar(255),
    location varchar(255)
);

CREATE TABLE IF NOT EXISTS Routes (
	route_id serial primary key, 
	from_station_id int references Stations(station_id), 
	to_station_id int references Stations(station_id), 
    distance int
);

CREATE TABLE IF NOT EXISTS Schedules (
	schedule_id serial primary key, 
	train_id int references Trains(train_id), 
	route_id int references Routes(route_id),
	departure_time timestamp, 
	arrival_time timestamp
);

CREATE TABLE IF NOT EXISTS StationVisit (
	station_visit_id serial primary key,
	schedule_id int references Schedules(schedule_id), 
	station_id int references Stations(station_id), 
	station_order int,
	arrival_time timestamp,
	departure_time timestamp
);

CREATE TABLE IF NOT EXISTS Carriages (
	carriage_id serial primary key,
	train_id int references Trains(train_id), 
	number int,
	capacity int,
	carriage_class_id int references CarriageClasses(carriage_class_id)
);

CREATE TABLE IF NOT EXISTS Seats (
	seat_id serial primary key,
	carriage_id int references Carriages(carriage_id), 
	number int,
	description varchar(255),
	availability varchar(255)
);
