import pymysql
import time

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


def create_column_tech():
    connection = connection_init()
    query = 'ALTER TABLE users ADD COLUMN user_id_str VARCHAR(40);'
    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
    finally:
        connection.commit()
        connection.close()

def copy_user_tech():
    connection = connection_init()
    query = 'SELECT user_id FROM users;'
    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchall()
    finally:
        connection.commit()
        connection.close()
    for user in result:
        user_id_str = str(user['user_id'])
        print(user_id_str)
        connection = connection_init()
        query = 'UPDATE users SET user_id_str = %s WHERE user_id = %s;'
        query_tuple = (user_id_str, int(user_id_str))
        try:
            with connection.cursor() as cursor:
                cursor.execute(query, query_tuple)
        finally:
            connection.commit()
            connection.close()


def drop_column_tech():
    connection = connection_init()
    query = 'ALTER TABLE users DROP user_id;'
    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
    finally:
        connection.commit()
        connection.close()


def replace_column_tech():
    connection = connection_init()
    query = 'ALTER TABLE users MODIFY COLUMN user_id_str VARCHAR(40) AFTER id;'
    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
    finally:
        connection.commit()
        connection.close()

    connection = connection_init()
    query = 'ALTER TABLE users CHANGE COLUMN user_id_str user_id VARCHAR(40);'
    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
    finally:
        connection.commit()
        connection.close()





def sql_start():
    connection = connection_init()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                    CREATE TABLE IF NOT EXISTS events(
                    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT, 
                    title VARCHAR(60), 
                    dtime INT, 
                    capacity INT, 
                    location VARCHAR(100), 
                    photo_id VARCHAR(100), 
                    description VARCHAR(4000),
                    status VARCHAR(100))
                    """)
            cursor.execute("""
                    CREATE TABLE IF NOT EXISTS registrations(
                    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT, 
                    event_id VARCHAR(10), 
                    user_id INT, 
                    nick_name VARCHAR(40), 
                    real_name VARCHAR(40), 
                    number_persons INT, 
                    wish VARCHAR(20),
                    table_name VARCHAR(40));
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


async def create_user_sql(user_id, username):
    connection = connection_init()
    query = 'INSERT INTO users (user_id, nick_name) VALUES (%s, %s);'
    query_tuple = (user_id, username)
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, query_tuple)
    finally:
        connection.commit()
        connection.close()


async def create_event_sql(state):
    connection = connection_init()
    async with state.proxy() as data:
        title = data.as_dict()['title']
        dtime = str(data.as_dict()['dtime'])
        capacity = data.as_dict()['capacity']
        location = data.as_dict()['location']
        photo_id = data.as_dict()['photo_id']
        description = data.as_dict()['description']
    query = """
    INSERT INTO events (title, dtime, capacity, location, photo_id, description, status) 
    VALUES (%s, %s, %s, %s, %s, %s, %s);
    """

    query_tuple = (title, dtime, capacity, location, photo_id, description, 'upcoming')
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


async def get_tables_not_event(event_id):
    connection = connection_init()
    query = """
        SELECT table_name
        FROM tables
        WHERE table_name NOT IN (
        SELECT table_name FROM registrations
        WHERE event_id = %s)
        """
    query_tuple = (event_id,)
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, query_tuple)
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

async def get_user_events_sql():
    connection = connection_init()
    query = 'SELECT * FROM events WHERE status = "upcoming";'
    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchall()
    finally:
        connection.commit()
        connection.close()
        return result


async def get_event_id_sql(id):
    connection = connection_init()
    query = 'SELECT * FROM events WHERE id = %s;'
    query_tuple = (id,)
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, query_tuple)
            result = cursor.fetchone()
            return result
    finally:
        connection.commit()
        connection.close()


async def create_registration_sql(state):
    async with state.proxy() as data:
        event_id = data.as_dict()['event_id']
        user_id = data.as_dict()['user_id']
        nick_name = data.as_dict()['nick_name']
        number_persons = data.as_dict()['persons']
        wish = data.as_dict()['wish']
        table_name = data.as_dict()['table']
    connection = connection_init()
    query = """
        INSERT INTO registrations 
        (event_id, user_id, nick_name, number_persons, wish, table_name) 
        VALUES (%s, %s, %s, %s, %s, %s);
        """
    query_tuple = (event_id, user_id, nick_name, number_persons, wish, table_name)
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, query_tuple)
    finally:
        connection.commit()
        connection.close()

async def is_registrated_sql(user_id, event_id):
    connection = connection_init()
    query = 'SELECT * FROM registrations WHERE user_id = %s AND event_id = %s;'
    query_tuple = (user_id, event_id)
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, query_tuple)
            response = cursor.fetchall()
            if len(response) == 0:
                result = False
            else:
                result = True
            return result
    finally:
        connection.commit()
        connection.close()


async def get_user_registrations(user_id):
    now = time.time() - 3600
    connection = connection_init()
    query = """
        SELECT *
        FROM events
        INNER JOIN registrations ON events.id = registrations.event_id
        WHERE registrations.user_id = %s AND events.dtime > %s;
        """
    query_tuple = (user_id, now)
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, query_tuple)
            response = cursor.fetchall()
            return response
    finally:
        connection.commit()
        connection.close()


async def get_reg_persons(event_id, user_id):
    connection = connection_init()
    query = 'SELECT number_persons FROM registrations WHERE event_id = %s AND user_id = %s;'
    query_tuple = (event_id, user_id)
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, query_tuple)
            response = cursor.fetchone()
            return response
    finally:
        connection.commit()
        connection.close()


async def get_reg_persons_reg_id(reg_id):
    connection = connection_init()
    query = 'SELECT number_persons FROM registrations WHERE id = %s;'
    query_tuple = (reg_id)
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, query_tuple)
            response = cursor.fetchone()
            return response
    finally:
        connection.commit()
        connection.close()


async def edit_persons_sql(event_id, user_id, persons):
    connection = connection_init()
    query = 'UPDATE registrations SET number_persons = %s WHERE event_id = %s AND user_id = %s;'
    query_tuple = (persons, event_id, user_id)
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, query_tuple)
    finally:
        connection.commit()
        connection.close()


async def edit_persons_reg_id_sql(reg_id, persons):
    connection = connection_init()
    query = 'UPDATE registrations SET number_persons = %s WHERE id = %s;'
    query_tuple = (persons, reg_id)
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, query_tuple)
    finally:
        connection.commit()
        connection.close()


async def delete_registration_sql(event_id, user_id):
    connection = connection_init()
    query = 'DELETE FROM registrations WHERE event_id = %s AND user_id = %s;'
    query_tuple = (event_id, user_id)
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, query_tuple)
    finally:
        connection.commit()
        connection.close()


async def delete_registration_reg_id_sql(reg_id):
    connection = connection_init()
    query = 'DELETE FROM registrations WHERE id = %s;'
    query_tuple = (reg_id,)
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, query_tuple)
    finally:
        connection.commit()
        connection.close()

async def get_event_capacity_sql(event_id):
    connection = connection_init()
    query = 'SELECT capacity FROM events WHERE id = %s;'
    query_tuple = (event_id,)
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, query_tuple)
            response = cursor.fetchone()
            return response
    finally:
        connection.commit()
        connection.close()

async def get_total_regs_sql(event_id):
    connection = connection_init()
    query = 'SELECT SUM(number_persons), COUNT(id) FROM registrations WHERE event_id = %s;'
    query_tuple = (event_id,)
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, query_tuple)
            response = cursor.fetchone()
            return response
    finally:
        connection.commit()
        connection.close()


async def get_admin_events_sql():
    connection = connection_init()
    timestamp_limit = time.time() - 604800
    query = 'SELECT * FROM events WHERE dtime > %s;'
    query_tuple = (timestamp_limit,)
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, query_tuple)
            result = cursor.fetchall()
            return result
    finally:
        connection.commit()
        connection.close()


async def get_event_users_sql(event_id):
    connection = connection_init()
    query = 'SELECT user_id FROM registrations WHERE event_id = %s;'
    query_tuple = (event_id,)
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, query_tuple)
            result = cursor.fetchall()
            return result
    finally:
        connection.commit()
        connection.close()


async def delete_event_sql(event_id):
    connection = connection_init()
    query = 'DELETE FROM events WHERE id = %s'
    query_tuple = (event_id,)
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, query_tuple)
    finally:
        connection.commit()
        connection.close()


async def delete_reg_event_sql(event_id):
    connection = connection_init()
    query = 'DELETE FROM registrations WHERE event_id = %s'
    query_tuple = (event_id,)
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, query_tuple)
    finally:
        connection.commit()
        connection.close()


async def edit_event_status_sql(event_id):
    connection = connection_init()
    query = 'UPDATE events SET status = "past" WHERE id = %s;'
    query_tuple = (event_id,)
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, query_tuple)
    finally:
        connection.commit()
        connection.close()


async def get_list_sql(event_id):
    connection = connection_init()
    query = 'SELECT * FROM registrations LEFT JOIN users USING (user_id) WHERE event_id = %s ORDER BY wish DESC;'
    query_tuple = (event_id,)
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, query_tuple)
            result = cursor.fetchall()
            return result
    finally:
        connection.commit()
        connection.close()


async def get_users_sql():
    connection = connection_init()
    query = 'SELECT user_id FROM users'
    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchall()
            return result
    finally:
        connection.commit()
        connection.close()


async def is_user_sql(user_id):
    connection = connection_init()
    query = 'SELECT * FROM users WHERE user_id = %s'
    query_tuple = (user_id,)
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, query_tuple)
            result = cursor.fetchall()
            if len(result) == 0:
                return False
            else:
                return True
    finally:
        connection.commit()
        connection.close()