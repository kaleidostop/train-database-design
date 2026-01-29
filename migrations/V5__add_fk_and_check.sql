ALTER TABLE Bookings
ADD COLUMN IF NOT EXISTS schedule_id int;

DO $$
BEGIN
    BEGIN
        ALTER TABLE Bookings
        ADD CONSTRAINT bookings_schedule_fk
        FOREIGN KEY (schedule_id) REFERENCES Schedules(schedule_id)
        NOT VALID;
    EXCEPTION WHEN duplicate_object THEN
        NULL;
    END;

    BEGIN
        ALTER TABLE public.bookings
        VALIDATE CONSTRAINT bookings_schedule_fk;
    EXCEPTION WHEN undefined_object THEN
        NULL;
    END;
END$$;

DO $$
BEGIN
    BEGIN
        ALTER TABLE Reviews
            ADD CONSTRAINT reviews_stars_check
            CHECK (stars BETWEEN 1 AND 5) NOT VALID;
        EXCEPTION WHEN duplicate_object THEN
            NULL;
    END;

    BEGIN
        ALTER TABLE Reviews
        VALIDATE CONSTRAINT reviews_stars_check;
    EXCEPTION WHEN undefined_object THEN
        NULL;
    END;
END$$;