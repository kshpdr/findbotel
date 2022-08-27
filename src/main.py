import asyncio

import local_config as config
#import env_config as config
import telebot
from flask import Flask, request
import os
import logging
from SearchInfo import SearchInfo
from Database import Database
from AsyncDatabase import *
from MarkupGenerator import MarkupGenerator
from unique_data import *
from telebot.types import LabeledPrice, ShippingOption

prices = [LabeledPrice(label='Hotel Five Stars Riveera', amount=125050), LabeledPrice('Gift wrapping', 500)]

bot = telebot.TeleBot(config.telegram_token)

journey_to_find = SearchInfo()
database = Database(config.DATABASE_URL)
markup_generator = MarkupGenerator()


@bot.message_handler(commands=['start'])
def start_command(message):
    msg = bot.reply_to(message, "Let's start new search! Simply type your answer, "
                                "by multiple options just separate them with commas, "
                                "or choose ones from the list. \n \n"
                                "What is a *departure airport(s)*? \n"
                                "e.g. 'Berlin,Frankfurt'",
                       parse_mode="Markdown",
                       reply_markup=markup_generator.generate_markup_from_word("List of airports", "departureairports"))
    bot.register_next_step_handler(msg, process_flight_from)


# TODO: add a markup with list of airports and pagination
def process_flight_from(message):
    flight_from = message.text.split(",")
    try:
        journey_to_find.set_flight_from(flight_from)
        msg = bot.reply_to(message, 'What is a *arrival airport*?',
                           parse_mode="Markdown",
                           reply_markup=markup_generator.generate_markup_from_word("List of airports", "arrivalairports"))
        bot.register_next_step_handler(msg, process_flight_to)
    except Exception as e:
        msg = bot.reply_to(message, f'Oops, there is no airport with name(s) {str(e)}. Try again!')
        bot.register_next_step_handler(msg, process_flight_from)


def process_flight_to(message):
    flight_to = message.text.split(",")
    try:
        journey_to_find.set_flight_to(flight_to)
        msg = bot.reply_to(message, 'What is the *start date*? \n'
                                    'E.g. 29.09.2022', parse_mode="Markdown")
        bot.register_next_step_handler(msg, process_start_date)
    except Exception as e:
        msg = bot.reply_to(message, f'Oops, there is no airport with name(s) {str(e)}. Try again!')
        bot.register_next_step_handler(msg, process_flight_to)


# TODO: add check for current_date > start_date
def process_start_date(message):
    start_date = message.text.split(".")
    try:
        journey_to_find.set_start_date(start_date)
        msg = bot.reply_to(message, 'What is the *end date*? \n'
                                    'E.g. 13.10.2022', parse_mode="Markdown")
        bot.register_next_step_handler(msg, process_end_date)
    except Exception as e:
        msg = bot.reply_to(message, f'Oops, date was sent in a wrong format. Try again!')
        bot.register_next_step_handler(msg, process_start_date)


# TODO: add check for end_date > start_date
def process_end_date(message):
    end_date = message.text.split(".")
    try:
        journey_to_find.set_end_date(end_date)
        msg = bot.reply_to(message, 'How many adults are going? E.g. 2', parse_mode="Markdown")
        bot.register_next_step_handler(msg, process_adults)
    except Exception as e:
        msg = bot.reply_to(message, str(e))
        bot.register_next_step_handler(msg, process_end_date)


# TODO: add simple int checks
def process_adults(message):
    adults = message.text
    journey_to_find.set_adults(adults)
    msg = bot.reply_to(message, 'How many children are going? E.g. 1')
    bot.register_next_step_handler(msg, process_kids)


def process_kids(message):
    kids = message.text
    journey_to_find.set_kids(kids)
    msg = bot.reply_to(message, 'Thanks! We are searching for a best journey for you...')
    make_search(msg)
    #journey_to_find.offers = database.find_offers(search_info=journey_to_find)


def make_search(message):
    offers = asyncio.run(call_find_journey(journey_to_find))
    offers = [offer.set_hotel(Hotel(*list(asyncio.run(call_find_hotel(offer))))) for offer in offers]
    journey_to_find.set_offers(offers)
    bot.send_photo(message.chat.id,
                   photo=open(offers[0].photo_path, "rb"),
                   caption=offers[0],
                   reply_markup=markup_generator.generate_markup_for_hotels())
    print(offers[0])


# CALLBACK QUERIES
@bot.callback_query_handler(func=lambda call: call.data =='previous')
def show_previous_hotel(call):
    journey_to_find.current_offer = (journey_to_find.current_offer - 1) % len(journey_to_find.offers)
    bot.delete_message(
        call.message.chat.id,
        call.message.message_id
    )
    bot.send_photo(call.message.chat.id,
                   photo=open(journey_to_find.offers[journey_to_find.current_offer].photo_path, "rb"),
                   caption=journey_to_find.offers[journey_to_find.current_offer],
                   reply_markup=markup_generator.generate_markup_for_hotels())


@bot.callback_query_handler(func=lambda call: call.data =='next')
def show_next_hotel(call):
    journey_to_find.current_offer = (journey_to_find.current_offer + 1) % len(journey_to_find.offers)
    bot.delete_message(
        call.message.chat.id,
        call.message.message_id
    )
    bot.send_photo(call.message.chat.id,
                   photo=open(journey_to_find.offers[journey_to_find.current_offer].photo_path, "rb"),
                   caption=journey_to_find.offers[journey_to_find.current_offer],
                   reply_markup=markup_generator.generate_markup_for_hotels())

@bot.callback_query_handler(func=lambda call: call.data =='pay')
def start_payment(call):
    bot.send_invoice(
        call.message.chat.id,  # chat_id
        'A wonderful trip to Palma de Mallorca',  # title
        'Tired of work? Wanna have a little rest of the busy town? Children are yelling without stopping? Book a flight to Mallorca right now and finally get some nice holidays!',
        # description
        'HAPPY FRIDAYS COUPON',  # invoice_payload
        "284685063:TEST:NDY4ZTJlOTA4Yjgw",  # provider_token
        'eur',  # currency
        prices,  # prices
        photo_url='https://img.welt.de/img/reise/mobile240376829/5042501447-ci102l-w1024/Beach-and-bay-with-turquoise-sea-water-Cala-des-Moro-Mallorca.jpg',
        photo_height=512,  # !=0/None or picture won't be shown
        photo_width=512,
        is_flexible=False,  # True If you need to set up Shipping Fee
        start_parameter='time-machine-example')


@bot.callback_query_handler(func=lambda call: call.data =='maps')
def send_location(call):
    bot.send_location(call.message.chat.id,
                      latitude=journey_to_find.offers[journey_to_find.current_offer].hotel.latitude,
                      longitude=journey_to_find.offers[journey_to_find.current_offer].hotel.longitude)


@bot.callback_query_handler(func=lambda call: call.data =='departureairports')
def show_departure_airports(call):
    bot.send_message(call.message.chat.id,
                     "Here is a list of all departure airports. Choose one(s) that you need!",
                     reply_markup=markup_generator.generate_markup_from_dict(outbounddepartureairports))


@bot.callback_query_handler(func=lambda call: call.data.split('#')[0]=='page')
def characters_page_callback(call):
    page = int(call.data.split('#')[1])
    bot.delete_message(
        call.message.chat.id,
        call.message.message_id
    )
    bot.send_message(call.message.chat.id,
                     "Here is a list of all departure airports. Choose one(s) that you need!",
                     reply_markup=markup_generator.generate_markup_from_dict(outbounddepartureairports,
                                                                             page,
                                                                             journey_to_find.flight_from))


@bot.callback_query_handler(func=lambda call: call.data[0] != "✔")
def change_departure_airport(call):
    airport_full = call.data
    airport_code = call.data[-4:-1]  # "Airport (PLZ)" -> PLZ
    if airport_code not in journey_to_find.flight_from:
        journey_to_find.add_airport_to_flight_from(airport_code)
        new_markup = markup_generator.add_airport_to_markup(call.message.reply_markup, airport_full)
    else:
        journey_to_find.delete_airport_to_flight_from(airport_code)
        new_markup = markup_generator.delete_airport_to_markup(call.message.reply_markup, airport_full)
    bot.edit_message_text("Here is a list of all departure airports. Choose one(s) that you need!",
                          chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          reply_markup=new_markup)


# check if heroku variable is in the environment
if "HEROKU" in list(os.environ.keys()):
    logger = telebot.logger
    telebot.logger.setLevel(logging.INFO)

    server = Flask(__name__)

    @server.route("/", methods=['POST'])
    def getMessage():
        bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
        return "!", 200

    @server.route("/")
    def webhook():
        bot.remove_webhook()
        bot.set_webhook(url=config.app_url)
        return "?", 200
    server.run(host="0.0.0.0", port=os.environ.get('PORT', 80))
else:
    # without heroku variable local use
    # delete webhook and use long polling
    bot.remove_webhook()
    bot.polling(none_stop=True)