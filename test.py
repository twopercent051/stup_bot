import pymysql

from create_bot import config

import time
from datetime import datetime
date_str = 1671136148.4853342
time_tuple_gm = time.gmtime(date_str)
time_tuple_local = time.localtime(date_str)
print(time_tuple_gm)
print(time_tuple_local)
print(time.time())

# def connection_init():
#     host = config.db.host
#     user = config.db.user
#     password = config.db.password
#     db_name = config.db.database
#     connection = pymysql.connect(
#         host=host,
#         port=3306,
#         user=user,
#         password=password,
#         database=db_name,
#         cursorclass=pymysql.cursors.DictCursor
#     )
#     return connection
#
#
# def create_table_sql():
#     connection = connection_init()
#     query = 'DELETE FROM events WHERE id = 3;'
#     # query_tuple = (table,)
#     try:
#         with connection.cursor() as cursor:
#             cursor.execute(query)
#     finally:
#         connection.commit()
#         connection.close()


# create_table_sql()