import pymysql

from create_bot import config




def connection_init():
    host = config.db.host
    user = config.db.user
    password = config.db.password
    db_name = config.db.database
    connection = pymysql.connect(
        host=host,
        port=3306,
        user=user,
        password=password,
        database=db_name,
        cursorclass=pymysql.cursors.DictCursor
    )
    return connection


def sql_start():
    connection = connection_init()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                    CREATE TABLE IF NOT EXISTS events(
                    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT, 
                    title VARCHAR(40), 
                    date VARCHAR(20), 
                    time VARCHAR(10), 
                    location VARCHAR(100), 
                    photo_id VARCHAR(100), 
                    description VARCHAR(4000))
                    """)
            cursor.execute("""
                    CREATE TABLE IF NOT EXISTS registrations(
                    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT, 
                    event_id VARCHAR(10), 
                    user_id INT, 
                    nick_name VARCHAR(40), 
                    real_name VARCHAR(40), 
                    number_persons INT, 
                    wish VARCHAR(20))
                    """)
            cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users(
                    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT, 
                    user_id INT, 
                    nick_name VARCHAR(40))
                    """)
            cursor.execute("""
                    CREATE TABLE IF NOT EXISTS tables(
                    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT, 
                    table_name VARCHAR(40))
                    """)
            cursor.execute("ALTER TABLE events CONVERT TO CHARACTER SET utf8mb4")
            cursor.execute("ALTER TABLE registrations CONVERT TO CHARACTER SET utf8mb4")
            cursor.execute("ALTER TABLE users CONVERT TO CHARACTER SET utf8mb4")
            cursor.execute("ALTER TABLE tables CONVERT TO CHARACTER SET utf8mb4")
    finally:
        connection.close()


async def create_event_sql(state):
    connection = connection_init()
    async with state.proxy() as data:
        title = data.as_dict()['title']
        date = data.as_dict()['date']
        time = data.as_dict()['time']
        location = data.as_dict()['location']
        photo_id = data.as_dict()['photo_id']
        description = data.as_dict()['description']
    query = 'INSERT INTO events (title, date, time, location, photo_id, description) VALUES (%s, %s, %s, %s, %s, %s);'
    query_tuple = (title, date, time, location, photo_id, description)
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, query_tuple)
    finally:
        connection.commit()
        connection.close()


async def get_tables():
    connection = connection_init()
    query = 'SELECT table_name FROM tables;'
    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchall()
    finally:
        connection.commit()
        connection.close()
        return result


async def create_table_sql(table):
    connection = connection_init()
    query = 'INSERT INTO tables (table_name) VALUES (%s);'
    query_tuple = (table,)
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, query_tuple)
    finally:
        connection.commit()
        connection.close()

async def delete_tables_sql():
    connection = connection_init()
    query = 'DELETE FROM tables;'
    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
    finally:
        connection.commit()
        connection.close()