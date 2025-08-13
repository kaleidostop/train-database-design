import os
import time
import random
import psycopg2
from faker import Faker
from collections import deque, defaultdict

app_env = os.getenv('APP_ENV', 'prod')
seed_count = int(os.getenv('SEED_COUNT', '10'))
db_host = os.getenv('DB_HOST', 'postgres_db')
db_port = os.getenv('DB_PORT', '5432')
db_name = os.getenv('DB_NAME', 'mydb')
db_user = os.getenv('DB_USER', 'myuser')
db_password = os.getenv('DB_PASSWORD', 'mypass')

faker = Faker("ru_RU")

def wait_for_pg():
    while True:
        try:
            conn = psycopg2.connect(
                host=db_host, port=db_port,
                user=db_user, password=db_password, dbname=db_name
            )
            conn.close()
            return
        except psycopg2.OperationalError:
            print("Seeder: Waiting for Postgres...")
            time.sleep(2)

def get_tables(cur):
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables
        WHERE table_schema = 'public'
        AND table_type = 'BASE TABLE'
        AND table_name <> 'flyway_schema_history';
    """)
    return [r[0] for r in cur.fetchall()]

def get_dependencies(cur):
    cur.execute("""
        SELECT 
            tc.table_name AS child_table,
            ccu.table_name AS parent_table
        FROM information_schema.table_constraints AS tc
        JOIN information_schema.key_column_usage AS kcu
            ON tc.constraint_name = kcu.constraint_name
        JOIN information_schema.constraint_column_usage AS ccu
            ON ccu.constraint_name = tc.constraint_name
        WHERE constraint_type = 'FOREIGN KEY';
    """)
    graph = defaultdict(set)
    for child, parent in cur.fetchall():
        graph[parent].add(child)
    return graph

def topsort(tables, graph):
    in_deg = {t: 0 for t in tables}
    for p in graph:
        for c in graph[p]:
            in_deg[c] += 1

    queue = deque([t for t in tables if in_deg[t] == 0])
    order = []

    while queue:
        node = queue.popleft()
        order.append(node)
        for c in graph[node]:
            in_deg[c] -= 1
            if in_deg[c] == 0:
                queue.append(c)
    return order

def generate_value(col_name, col_type):
    if col_name == 'name':
        return faker.name()
    elif col_type in ('character varying', 'text'):
        return faker.sentence(nb_words=3)
    elif col_type in ('numeric', 'integer', 'smallint', 'bigint'):
        return random.randint(1, 1000)
    elif col_type in ('timestamp without time zone', 'timestamp with time zone', 'date'):
        return fake.date_between(start_date="-1y", end_date="today")
    else:
        return None

def seed_table(cur, table):
    cur.execute("""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = %s
        AND column_name NOT LIKE %s
        ORDER BY ordinal_position;    
        """, (table, '%id'))
    columns = cur.fetchall()

    if not columns:
        print(f"В таблице {table} нет колонок")

    col_names = [c[0] for c in columns]
    placeholders = ", ".join(["%s"] * len(columns))
    insert_sql = f"INSERT INTO {table} ({', '.join(col_names)}) VALUES ({placeholders})"

    for _ in range(seed_count):
        values = []
        for col_name, col_type in columns:
            values.append(generate_value(col_name, col_type))
        cur.execute(insert_sql, values)


def seed_all_tables(cur):
    tables = get_tables(cur)
    for table in tables:
        seed_table(cur, table)


if __name__ == "__main__":
    print("Производится сидирование...")

    if app_env != 'dev':
        print("Сидирование доступно только в режиме разработки")
        exit(0)

    try:
        wait_for_pg()

        conn = psycopg2.connect(
            dbname=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port
        )
        cur = conn.cursor()

        tables = get_tables(cur)
        graph = get_dependencies(cur)
        order = topsort(tables, graph)

        for t in reversed(order):
            cur.execute(f"TRUNCATE TABLE {t} RESTART IDENTITY CASCADE;")
            print(f"Таблица {t} очищена")

        for t in order:
            seed_table(cur, t)
            print(f"Добавлено {seed_count} записей в таблицу {t}.")

        conn.commit()
        cur.close()
        conn.close()

        print("Сидирование завершено")

    except Exception as e:
        print(f"Ошибка сидирования: {e}")
        exit(1)