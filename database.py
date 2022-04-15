import sqlite3

def sql_table():
    with sqlite3.connect('playersID.db') as conn:
        cursor = conn.cursor()
        query = """ CREATE TABLE IF NOT EXISTS expenses(ID_discord TEXT, nickFI TEXT, player_id TEXT, ID_chanell_discord) """
        cursor.execute(query)

