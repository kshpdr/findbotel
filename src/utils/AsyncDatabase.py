import psycopg
from models.SearchInfo import SearchInfo
from models.Offer import Offer
from local_config import *
#from env_config import *


async def find_journey(search_info: SearchInfo):
    async with await psycopg.AsyncConnection.connect(DATABASE_URL, sslmode='require') as aconn:
        async with aconn.cursor() as cur:
            flight_from = format_airports(search_info.flight_from)
            flight_to = format_airports(search_info.flight_to)
            query = f"""SELECT * FROM offers WHERE
                    outbounddepartureairport IN {flight_from} AND
                    outboundarrivalairport IN {flight_to} AND
                    departuredate LIKE '%{str(search_info.start_date.date())}%' AND
                    returndate LIKE '%{str(search_info.end_date.date())}%' AND
                    countadults = '{search_info.adults}' AND
                    countchildren = '{search_info.kids}';"""
            await cur.execute(query)
            return await cur.fetchall()


async def find_hotel(offer: Offer):
    async with await psycopg.AsyncConnection.connect(DATABASE_URL, sslmode='require') as aconn:
        async with aconn.cursor() as cur:
            query = f"""SELECT * FROM hotels WHERE id = '{offer.hotelid}'"""
            await cur.execute(query)
            return await cur.fetchone()


async def find_journey_from_departure_airport(search_info: SearchInfo):
    async with await psycopg.AsyncConnection.connect(DATABASE_URL, sslmode='require') as aconn:
        async with aconn.cursor() as cur:
            query = f"""SELECT * FROM offers WHERE
                    outbounddepartureairport = '{search_info.flight_from[0]}';"""
            await cur.execute(query)
            return await cur.fetchone()


async def find_journey_for_hotel(search_info: SearchInfo):
    async with await psycopg.AsyncConnection.connect(DATABASE_URL, sslmode='require') as aconn:
        async with aconn.cursor() as cur:
            query = f"""SELECT * FROM offers WHERE
                    outbounddepartureairport = '{search_info.flight_from[0]}' AND
                    outboundarrivalairport = '{search_info.flight_to[0]}' AND
                    departuredate LIKE '%{str(search_info.start_date.date())}%' AND
                    returndate LIKE '%{str(search_info.end_date.date())}%' AND
                    countadults = '{search_info.adults}' AND
                    countchildren = '{search_info.kids}' AND 
                    hotelid = '{search_info.offers[search_info.current_offer].hotelid}';"""
            # query2 = f"""SELECT * FROM offers WHERE
            #         outbounddepartureairport = 'BER'
            #         LIMIT 10;"""
            await cur.execute(query)
            return await cur.fetchall()


def format_airports(flight_from):
    line = "("
    for i in range(len(flight_from)):
        if i == len(flight_from) - 1:
            line += f"'{flight_from[i]}'"
            line += ")"
        else:
            line += f"'{flight_from[i]}', "
    return line