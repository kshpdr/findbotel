import local_config as config
#import env_configs as config
import psycopg2

conn = psycopg2.connect(config.DATABASE_URL, sslmode='require')
cur = conn.cursor()


class Database:
    def __init__(self, db_url):
        self.conn = psycopg2.connect(db_url, sslmode='require')
        self.cur = self.conn.cursor()

    def query(self, query):
        self.cur.execure(query)

    def close(self):
        self.cur.close()
        self.conn.close()

    def reviews_in_total(self):
        cur.execute("SELECT COUNT(*) FROM reviews")
        row = cur.fetchone()
        return row[0]

    def find_unique_flight_from(self):
        cur.execute("SELECT DISTINCT inbounddepartureairport FROM offers")
        row = cur.fetchone()
        return row