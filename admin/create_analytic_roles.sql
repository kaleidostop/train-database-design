SET app.analyst_names = :"ANALYST_NAMES";

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'analytic') THEN
        CREATE ROLE analytic NOLOGIN;
    END IF;
END$$;

GRANT CONNECT ON DATABASE :"DBNAME" TO analytic;
GRANT USAGE ON SCHEMA public TO analytic;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO analytic;
GRANT SELECT ON ALL SEQUENCES IN SCHEMA public TO analytic;

ALTER DEFAULT PRIVILEGES IN SCHEMA public 
    GRANT SELECT ON TABLES TO analytic;
ALTER DEFAULT PRIVILEGES IN SCHEMA public 
    GRANT SELECT ON SEQUENCES TO analytic;

DO $$
DECLARE
    usernames text[];
    uname text;
BEGIN
    usernames := string_to_array(current_setting('app.analyst_names', true), ',');

    FOREACH uname IN ARRAY usernames LOOP
        IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = uname) THEN
            EXECUTE format('CREATE USER %I WITH PASSWORD %L IN ROLE analytic', uname, uname || '_123');
        END IF;
    END LOOP;
END$$;    
