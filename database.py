import sqlite3
from sqlite3 import Error

def sql_table(conn):
    with sqlite3.connect('playersID.db') as conn:
        cursor = conn.cursor()
        cursor.execute()

