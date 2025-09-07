ALTER TABLE Trains 
RENAME COLUMN type TO type_id;

ALTER TABLE Trains
DROP COLUMN total_carriages,
DROP COLUMN total_seats,
ADD COLUMN name varchar(255);

ALTER TABLE Carriages
DROP COLUMN capacity;

ALTER TABLE AgeCategories 
DROP COLUMN price;