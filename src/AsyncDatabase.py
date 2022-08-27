import asyncio

import psycopg
from SearchInfo import SearchInfo
from Offer import Offer
from Hotel import Hotel
from local_config import *


async def find_journey(search_info: SearchInfo):
    async with await psycopg.AsyncConnection.connect(DATABASE_URL, sslmode='require') as aconn:
        async with aconn.cursor() as cur:
            # query = f"""SELECT * FROM offers WHERE
            #         outbounddepartureairport = '{search_info.flight_from[0]}' AND
            #         outboundarrivalairport = '{search_info.flight_to[0]}' AND
            #         departuredate LIKE '%{str(search_info.start_date.date())}%' AND
            #         returndate LIKE '%{str(search_info.end_date.date())}%' AND
            #         countadults = '{search_info.adults}' AND
            #         countchildren = '{search_info.kids}'
            #         LIMIT 10;"""
            query2 = f"""SELECT * FROM offers WHERE
                    outbounddepartureairport = 'BER'
                    LIMIT 10;"""
            print(query2)
            await cur.execute(query2)
            offers = [Offer(*list(raw_offer)) for raw_offer in await cur.fetchall()]
            return offers


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


async def call_find_journey(search_info):
    offers = await asyncio.gather(find_journey(search_info))
    return offers[0]


async def call_find_hotel(offer: Offer):
    hotel_info = await asyncio.gather(find_hotel(offer))
    return hotel_info[0]