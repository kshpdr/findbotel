import psycopg
from models.SearchInfo import SearchInfo
from models.Offer import Offer


class Database:
    def __init__(self, db_url):
        self.conn = psycopg.connect(db_url, sslmode='require')
        self.cur = self.conn.cursor()

    def close(self):
        self.cur.close()
        self.aconn.close()

    def find_journey(self, search_info: SearchInfo):
        flight_from = self.format_airports(search_info.flight_from)
        flight_to = self.format_airports(search_info.flight_to)
        query = f"""SELECT * FROM offers2 INNER JOIN hotels ON hotels.id = offers2.hotelid WHERE
                                    outbounddepartureairport IN {flight_from} AND
                                    outboundarrivalairport IN {flight_to} AND
                                    departuredate = '{str(search_info.start_date.date())}' AND
                                    returndate = '{str(search_info.end_date.date())}' AND
                                    countadults = {int(search_info.adults)} AND
                                    countchildren = {int(search_info.kids)};"""
        self.cur.execute(query)
        return self.cur.fetchall()

    def find_hotel(self, offer: Offer):
        query = f"""SELECT * FROM hotels WHERE id = '{offer.hotelid}'"""
        self.cur.execute(query)
        return self.cur.fetchone()

    def find_journey_for_hotel(self, search_info: SearchInfo):
        flight_from = self.format_airports(search_info.flight_from)
        flight_to = self.format_airports(search_info.flight_to)
        query = f"""SELECT * FROM offers2 INNER JOIN hotels ON hotels.id = offers2.hotelid WHERE
                            outbounddepartureairport IN {flight_from} AND
                            outboundarrivalairport IN {flight_to} AND
                            departuredate = '{str(search_info.start_date.date())}' AND
                            returndate = '{str(search_info.end_date.date())}' AND
                            countadults = {int(search_info.adults)} AND
                            countchildren = {int(search_info.kids)} AND 
                            hotelid = {search_info.offers[search_info.current_offer].hotelid};"""
        self.cur.execute(query)
        return self.cur.fetchall()

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