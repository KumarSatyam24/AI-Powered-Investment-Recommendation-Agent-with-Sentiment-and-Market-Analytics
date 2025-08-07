import psycopg2

def insert_stock_price(ticker, price, timestamp):
    conn = psycopg2.connect(host="localhost", port=8812, user="admin", password="quest")
    cur = conn.cursor()
    cur.execute(f"INSERT INTO stock_prices (ticker, price, ts) VALUES ('{ticker}', {price}, '{timestamp}')")
    conn.commit()
    conn.close()