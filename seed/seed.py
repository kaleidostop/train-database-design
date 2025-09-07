import os
import time
import random
import psycopg2
from faker import Faker
from collections import deque, defaultdict
import traceback

app_env = os.getenv('APP_ENV', 'prod')
seed_count = int(os.getenv('SEED_COUNT', '10'))
db_host = os.getenv('DB_HOST', 'postgres_db')
db_port = os.getenv('DB_PORT', '5432')
db_name = os.getenv('DB_NAME', 'mydb')
db_user = os.getenv('DB_USER', 'myuser')
db_password = os.getenv('DB_PASSWORD', 'mypass')

faker = Faker("ru_RU")

TABLE_SIZES = {
    "trains" : 1,
    "carriages" : 15,
    "seats" : 200,
    "routes" : 0.5,
    "schedules" : 10,
    "stations" : 10,
    "stationvisit" : 100,

    "accounts" : 250,
    "passengers" : 500,
    "bookings" : 1000,
    "bookedseats" : 2000,
    "prices" : 10,
    "reviews" : 2,
    "notifications" : 100,
    "travelhistory" : 1000,
    "payments" : 1000,
 
    "traintypes" : 0,
    "carriageclasses" : 0,
    "agecategories" : 0,
    "paymentmethods" : 0,
    "bookingstatus" : 0
}

# unique_columns = [("passengers", "document_number"), ("accounts", "passenger_id"), ("accounts", "email"), ("accounts", "phone"), ("stationvisit", "station_order")]

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

def get_fk_columns(cur):
    cur.execute("""
        SELECT
            tc.table_name AS child_table,
            kcu.column_name AS child_column,
            ccu.table_name AS parent_table,
            ccu.column_name AS parent_column
        FROM information_schema.table_constraints AS tc
        JOIN information_schema.key_column_usage AS kcu
            ON tc.constraint_name = kcu.constraint_name
        JOIN information_schema.constraint_column_usage AS ccu
            ON ccu.constraint_name = tc.constraint_name
        WHERE constraint_type = 'FOREIGN KEY';
    """)
    fk_cols = defaultdict(list)
    for child_table, child_col, parent_table, parent_col in cur.fetchall():
        fk_cols[child_table].append((child_col, parent_table, parent_col))
    return fk_cols


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

def generate_value(table, col_name, col_type):
    if col_type in ('character varying', 'text', 'char'):
        if col_name == 'full_name':
            return faker.name()
        elif col_name == 'phone':
            return faker.phone_number()  
        elif col_name == 'document_number':
            return faker.numerify('##########') 
        elif col_name == 'email':
           return faker.ascii_email()  
        elif col_name == 'password_hash':
            return faker.md5(raw_output=False) 
        elif col_name == 'gender':
            return random.choice(('м', 'ж'))
        elif col_name == 'location':
            return faker.city()
        elif col_name in ('description', 'commentary', 'message'):
            return faker.sentence()
        return faker.word()
    elif col_type in ('numeric', 'integer', 'smallint', 'bigint'):
        if col_name == 'stars':
            return random.randint(1, 5)
        return random.randint(1, 1000)
    elif col_type in ('timestamp without time zone', 'timestamp with time zone', 'date'):
        return faker.date_between(start_date="-1y", end_date="today")
    else:
        return None

def seed_table(cur, table, fk_columns, generated_fk_values):
    cur.execute("""
        SELECT column_name, data_type, column_default
        FROM information_schema.columns
        WHERE table_name = %s
        ORDER BY ordinal_position;    
        """, (table, ))
    columns = cur.fetchall()

    if not columns:
        print(f"В таблице {table} нет колонок")

    insert_columns = []
    for col_name, col_type, col_default in columns:
        if col_default and col_default.startswith("nextval"):  
            continue
        insert_columns.append((col_name, col_type))
    placeholders = ", ".join(["%s"] * len(insert_columns))
    insert_sql = f"INSERT INTO {table} ({', '.join(c[0] for c in insert_columns)}) VALUES ({placeholders}) RETURNING *;"

    multiplier = TABLE_SIZES.get(table, 1.0)
    if (multiplier == 0):
        table_size = 5
    else:
        table_size = int(seed_count * multiplier)
    for _ in range(table_size):
        values = []
        for col_name, col_type in insert_columns:
            fk_info = next((fk for fk in fk_columns.get(table, []) if fk[0] == col_name), None)
            if fk_info:
                parent_table, parent_col = fk_info[1], fk_info[2]
                #print(f"parent table: {parent_table}, parent col: {parent_col}")
                possible_values = generated_fk_values.get((parent_table, parent_col), [])
                if possible_values:
                    values.append(random.choice(possible_values))
                else:
                    values.append(None) 
            else:
                values.append(generate_value(table, col_name, col_type))

        cur.execute(insert_sql, values)
        inserted_row = cur.fetchone()

        for idx, (col_name, _, _) in enumerate(columns):
            if (table, col_name) in generated_fk_values:
                # print(f"table: {table}, col name: {col_name}")
                generated_fk_values[(table, col_name)].append(inserted_row[idx])
            # else:
            #     print(f"table: {table}, col name: {col_name} -- not FK")


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
        print("tables: ", *tables)
        dependencies = get_dependencies(cur)
        order = topsort(tables, dependencies)

        fk_columns = get_fk_columns(cur)
        generated_fk_values = {
            (fk[1], fk[2]) : []
            for fks in fk_columns.values()
            for fk in fks
        }
        
        # dict.fromkeys(
        #     ((fk[1], fk[2])  # parent_table, parent_column
        #     for fks in fk_columns.values()
        #     for fk in fks),
        #     []
        # )

        # print(*generated_fk_values.keys())

        for t in reversed(order):
            cur.execute(f"TRUNCATE TABLE {t} RESTART IDENTITY CASCADE;")
            print(f"Таблица {t} очищена")

        for t in order:
            seed_table(cur, t, fk_columns, generated_fk_values)
            print(f"Добавлено {seed_count} записей в таблицу {t}.")

        conn.commit()
        cur.close()
        conn.close()

        print("Сидирование завершено")

    except Exception as e:
        print(f"Ошибка сидирования: {e}", flush=True)
        traceback.print_exc()
        exit(1)