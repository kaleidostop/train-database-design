-- индекс для ускорения поиска пассажира по аккаунту
CREATE INDEX idx_passengers_account_id ON Passengers(account_id);

-- индекс для поиска бронирований по рейсу
CREATE INDEX idx_bookings_schedule_id ON Bookings(schedule_id);

-- индекс для поиска рейсов по поезду
CREATE INDEX idx_schedules_train_id ON Schedules(train_id);

-- индекс для поиска рейса по времени
CREATE INDEX idx_schedules_times ON Schedules(departure_time, arrival_time);

-- индекс для поиска бронирований по клиенту
CREATE INDEX idx_bookings_customer_id ON Bookings(customer_id);

-- индекс для получения пассажиров по бронированию
CREATE INDEX idx_bookedseats_booking_passenger ON BookedSeats(booking_id, passenger_id);

-- индекс для проверки занято ли место
CREATE INDEX idx_bookedseats_seat_id ON BookedSeats(seat_id);

-- индекс для поиск конкретного места в вагоне
CREATE UNIQUE INDEX idx_seats_carriage_number ON Seats(carriage_id, number);
