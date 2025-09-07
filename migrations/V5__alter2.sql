ALTER TABLE Bookings
ADD COLUMN schedule_id int references Schedules(schedule_id);