ALTER TABLE Bookings
ADD COLUMN IF NOT EXISTS schedule_id int references Schedules(schedule_id);

ALTER TABLE Reviews 
ADD CONSTRAINT stars_values CHECK (stars BETWEEN 1 AND 5);