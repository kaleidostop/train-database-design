CREATE TABLE IF NOT EXISTS Passengers (
    passenger_id serial primary key,
    full_name varchar(255),
    date_of_birth date,
    gender char(1),
    document_number varchar(10),
    age_category_id int references AgeCategories(age_category_id)
);

CREATE TABLE IF NOT EXISTS Accounts (
    account_id serial primary key,
    email varchar(255),
    phone varchar(20),
    password_hash varchar(255),
    passenger_id int references Passengers(passenger_id)
);

CREATE TABLE IF NOT EXISTS Prices (
    price_id serial primary key,
    schedule_id int references Schedules(schedule_id),
    carriage_class_id int references CarriageClasses(carriage_class_id),
    age_category_id int references AgeCategories(age_category_id),
    price int 
);

CREATE TABLE IF NOT EXISTS Payments (
    payment_id serial primary key,
    amount int,
    payment_method_id int references PaymentMethods(payment_method_id)
);

CREATE TABLE IF NOT EXISTS Bookings (
    booking_id serial primary key,
    customer_id int references Passengers(passenger_id),
    from_station_id int references Stations(station_id),
    to_station_id int references Stations(station_id),
    booking_date date,
    payment_id int references Payments(payment_id),
    status_id int references BookingStatus(booking_status_id)
);

CREATE TABLE IF NOT EXISTS BookedSeats (
    booked_seats_id serial primary key,
    booking_id int references Bookings(booking_id),
    passenger_id int references Passengers(passenger_id),
    seat_id int references Seats(seat_id)
);

CREATE TABLE IF NOT EXISTS Reviews (
    review_id serial primary key,
    account_id int references Accounts(account_id),
    train_id int references Trains(train_id),
    stars int,
    commentary varchar(255)
);

CREATE TABLE IF NOT EXISTS Notifications (
    notifications_id serial primary key,
    account_id int references Accounts(account_id),
    message varchar(255),
    status varchar(255),
    datetime timestamp
);

CREATE TABLE IF NOT EXISTS TravelHistory (
    travel_history_id serial primary key,
    passenger_id int references Passengers(passenger_id),
    train_id int references Trains(train_id),
    date date
);