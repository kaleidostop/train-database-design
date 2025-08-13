CREATE TABLE IF NOT EXISTS TrainTypes (
    train_types_id serial primary key,
    name varchar(255),
    description varchar(255)
);

CREATE TABLE IF NOT EXISTS CarriageClasses (
    carriage_class_id serial primary key,
    name varchar(255),
    description varchar(255)
);

CREATE TABLE IF NOT EXISTS AgeCategories (
  age_category_id serial primary key,
  name varchar(255),
  price decimal
);

CREATE TABLE IF NOT EXISTS PaymentMethods (
    payment_method_id serial primary key,
    name varchar(255),
    description varchar(255)
);

CREATE TABLE IF NOT EXISTS BookingStatus (
	booking_status_id serial primary key,
	name varchar(255)
);