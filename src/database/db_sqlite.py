import sqlite3

def init_sqlite():
    conn = sqlite3.connect("users.db")
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, risk_level TEXT
    )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS portfolios(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER, ticker TEXT
    )''')
    conn.commit()
    conn.close()