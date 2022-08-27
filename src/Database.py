import psycopg
from SearchInfo import SearchInfo
from Offer import Offer


class Database:
    def __init__(self, db_url):
        self.conn = psycopg.connect(db_url, sslmode='require')
        self.cur = self.conn.cursor()

    def query(self, query):
        self.cur.execute(query)

    def close(self):
        self.cur.close()
        self.aconn.close()

    def reviews_in_total(self):
        self.cur.execute("SELECT COUNT(*) FROM reviews")
        row = self.cur.fetchone()
        return row[0]

    def find_unique_flight_from(self):
        self.cur.execute("SELECT DISTINCT inbounddepartureairport FROM offers")
        row = self.cur.fetchone()
        return row

    def find_offers(self, search_info: SearchInfo):
        flight_from = self.format_airports(search_info.flight_from)
        flight_to = self.format_airports(search_info.flight_to)
        self.cur.execute(f"SELECT * FROM offers "
                         f"WHERE outbounddepartureairport IN {flight_from} "
                         f"AND outboundarrivalairport IN {flight_to} "
                         f"LIMIT 15;")
        raw = self.cur.fetchall()
        offers = [Offer(*list(raw_offer)) for raw_offer in raw]
        print(offers)

    def find_offers_from_departure_airport(self, departure_airport):
        self.cur.execute(f"SELECT * FROM haj "
                         f"WHERE outbounddepartureairport = '{departure_airport[0]}';")
        offers = [Offer(*list(raw_offer)) for raw_offer in self.cur.fetchall()]
        print("I GOT IT")
        return offers


    @staticmethod
    def format_airports(flight_from):
        line = "("
        for i in range(len(flight_from)):
            if i == len(flight_from) - 1:
                line += f"'{flight_from[i]}'"
                line += ")"
            else:
                line += f"'{flight_from[i]}', "
        return line