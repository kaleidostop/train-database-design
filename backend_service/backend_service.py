import os
import time
import psycopg2

db_host = os.getenv('DB_HOST', 'postgres_db')
db_port = os.getenv('DB_PORT', '5432')
db_name = os.getenv('DB_NAME', 'mydb')
db_user = os.getenv('DB_USER', 'myuser')
db_password = os.getenv('DB_PASSWORD', 'mypass')

QUERIES = [
    # число поездов
    "SELECT COUNT(*) FROM trains;",

    # какой аккаунт принадлежит данному пассажиру
    """
    SELECT account_id FROM Accounts 
    WHERE passenger_id = 123;
    """

    # сколько раз пассажиры ездили на поездах
    """
    SELECT p.full_name, COUNT(*) trips FROM Passengers p
    JOIN BookedSeats bs ON bs.passenger_id = p.passenger_id
    GROUP BY p.passenger_id;
    """

    # на скольких поездах ездили пассажиры
    """
    SELECT p.full_name, COUNT(t.train_id) num_trains FROM Passengers p
    JOIN BookedSeats bs ON bs.passenger_id = p.passenger_id
    JOIN Seats s ON bs.seat_id = s.seat_id 
    JOIN Carriages c ON c.carriage_id = s.carriage_id 
    JOIN Trains t ON t.train_id = c.carriage_id
    GROUP BY p.passenger_id; 
    """,

    # пассажиры, которые ездили одними рейсами с пассажиром с id=123
    """
    SELECT p2.passenger_id, p2.full_name, count(*) times
    FROM Passengers p2 
    JOIN BookedSeats bs2 ON p2.passenger_id = bs2.passenger_id
    JOIN Bookings b2 ON bs2.booking_id = b2.booking_id 
    WHERE p2.passenger_id != 123 AND b2.schedule_id IN (
        SELECT b1.schedule_id FROM Bookings b1
        JOIN BookedSeats bs1 ON bs1.booking_id = b1.booking_id
        WHERE bs1.passenger_id = 123
    ) GROUP BY p2.passenger_id ORDER BY times;
    """,
    
    """
    select t.train_id, c.carriage_id, count(s.seat_id) 
    from seats s 
    join carriages c on s.carriage_id=c.carriage_id 
    join trains t on t.train_id=c.train_id 
    group by t.train_id, c.carriage_id 
    order by t.train_id, c.carriage_id;
    """

    """
    select station_order, station_id 
    from stationvisit 
    where schedule_id=1;
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
        print(f"Ошибка работы бекенд-сервиса: {e}", flush=True)
        exit(1)