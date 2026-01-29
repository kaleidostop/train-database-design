import os
import time
import psycopg2

db_host = os.getenv('DB_HOST', 'postgres_db')
db_port = os.getenv('DB_PORT', '5432')
db_name = os.getenv('DB_NAME', 'mydb')
db_user = os.getenv('DB_USER', 'myuser')
db_password = os.getenv('DB_PASSWORD', 'mypass')

QUERIES = [

    # найти аккаунт по пассажиру
    """
    SELECT account_id FROM Accounts 
    WHERE passenger_id = 123;
    """,

    # найти пассажиров старше 18
    """
    SELECT p.passenger_id
    FROM Passengers p
    WHERE EXTRACT(YEAR FROM AGE(CURRENT_DATE, p.date_of_birth)) >= 18;
    """,

    # сколько мест в вагонах поездов
    """
    select t.train_id, c.carriage_id, count(s.seat_id) 
    from seats s 
    join carriages c on s.carriage_id=c.carriage_id 
    join trains t on t.train_id=c.train_id 
    group by t.train_id, c.carriage_id 
    order by t.train_id, c.carriage_id;
    """,

    # найти пассажиров данного рейса
    """
    select p.full_name FROM Passengers p
    JOIN BookedSeats bs ON p.passenger_id = bs.passenger_id
    JOIN Bookings b ON b.booking_id = bs.booking_id
    WHERE b.schedule_id = 123;
    """,

    # найти бронирования на заданные рейсы
    """
    SELECT *
    FROM Bookings
    WHERE schedule_id IN (10, 20, 30, 40);
    """,

    # найти рейсы данного поезда с сортировкой по времени
    """
    SELECT s.*
    FROM Schedules s
    WHERE s.train_id = 5
    ORDER BY s.departure_time;
    """,

    # найти рейсы из заданного окна времени
    """
    SELECT s.*
    FROM Schedules s
    WHERE s.departure_time >= DATE '2025-01-01'
    AND s.departure_time <  DATE '2025-10-01'
    """,

    # проверка занято ли данное место на данный рейс
    """
    SELECT 1
    FROM BookedSeats bs
    JOIN Bookings b ON b.booking_id = bs.booking_id
    WHERE b.schedule_id = 123
    AND bs.seat_id = 100
    LIMIT 1;
    """
]

def wait_for_pg():
    while True:
        try:
            conn = psycopg2.connect(
                host=db_host, port=db_port,
                user=db_user, password=db_password, dbname=db_name
            )
            conn.close()
            print("Соединение сервера с базой данных установлено")
            return
        except psycopg2.OperationalError:
            print("Backend service: Waiting for Postgres...")
            time.sleep(2)

def run_queries():
    conn = psycopg2.connect(
        host=db_host, port=db_port,
        user=db_user, password=db_password, dbname=db_name
    )
    cur = conn.cursor()

    print("Начата работа сервиса")
    while True:
        for q in QUERIES:
            start = time.time()
            cur.execute(q)
            rows = cur.fetchall()
            duration = time.time() - start
            print(f"Executed: {q[:40]}... in {duration:.3f}s, rows={len(rows)}")
        time.sleep(1)

if __name__ == "__main__":
    try:
        wait_for_pg()
        run_queries()
    
    except Exception as e:
        print(f"Ошибка работы бэкенд-сервиса: {e}", flush=True)
        exit(1)