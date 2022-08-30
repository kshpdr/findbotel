#import local_config as config
import env_config as config
import telebot
from flask import Flask, request
import os
import logging
from Database import Database
from AsyncDatabase import *
from MarkupGenerator import MarkupGenerator
from telebot.types import LabeledPrice

prices = [LabeledPrice(label='Hotel Five Stars Riveera', amount=125050), LabeledPrice('Gift wrapping', 500)]

bot = telebot.TeleBot(config.telegram_token)

journey_to_find = SearchInfo()
database = Database(config.DATABASE_URL)
markup_generator = MarkupGenerator()


# def register_handlers():
#     #bot.register_message_handler(start_command, commands=['start'], pass_bot=True)
#     bot.register_callback_query_handler(show_departure_airports, lambda call: call.data == 'departureairports', pass_bot=True)
#     bot.register_callback_query_handler(show_arrival_airports, lambda call: call.data == 'arrivalairports', pass_bot=True)
#     bot.register_callback_query_handler(ready_with_departure_airports, lambda call: call.data == 'departure_ready', pass_bot=True)
#     bot.register_callback_query_handler(ready_with_arrival_airports, lambda call: call.data == 'arrival_ready', pass_bot=True)
#
# register_handlers()

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


def process_flight_from(message):
    if message.text == "/start":
        start_command(message)
        return
    flight_from = message.text.split(",")
    try:
        journey_to_find.set_flight_from(flight_from)
        #asyncio.run(find_journey_from_departure_airport(journey_to_find))
        msg = bot.reply_to(message, 'What is a *arrival airport*?',
                           parse_mode="Markdown",
                           reply_markup=markup_generator.generate_markup_from_word("List of airports", "arrivalairports"))
        bot.register_next_step_handler(msg, process_flight_to)
    except Exception as e:
        msg = bot.reply_to(message, f'Oops, there is no airport with name(s) {str(e)}. Try again!')
        bot.register_next_step_handler(msg, process_flight_from)


def process_flight_to(message):
    flight_to = message.text.split(",")
    print(journey_to_find.flight_from)
    try:
        journey_to_find.set_flight_to(flight_to)
        msg = bot.reply_to(message, 'What is the *start date*? \n'
                                    'E.g. 29.09.2022', parse_mode="Markdown")
        bot.register_next_step_handler(msg, process_start_date)
    except Exception as e:
        msg = bot.reply_to(message, f'Oops, there is no airport with name(s) {str(e)}. Try again!')
        bot.register_next_step_handler(msg, process_flight_to)


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
    try:
        adults = message.text
        journey_to_find.set_adults(adults)
        msg = bot.reply_to(message, 'How many children are going? E.g. 1')
        bot.register_next_step_handler(msg, process_kids)
    except Exception as e:
        msg = bot.reply_to(message, str(e))
        bot.register_next_step_handler(msg, process_adults)


def process_kids(message):
    try:
        kids = message.text
        journey_to_find.set_kids(kids)
        msg = bot.reply_to(message, 'Thanks! We are searching for a best journey for you...')
        make_search(msg)
    except Exception as e:
        msg = bot.reply_to(message, str(e))
        bot.register_next_step_handler(msg, process_kids)

# TODO: cache all offers for all hotels
def make_search(message):
    try:
        start = time.time()
        print(f"started at {start}")
        raw_offers = asyncio.run(find_journey(journey_to_find))
        finish = time.time()
        print(f"finished at {finish}")
        print(finish - start)
        offers = [Offer(*list(raw_offer)) for raw_offer in raw_offers]
        offers = [offer.set_hotel(Hotel(*list(asyncio.run(find_hotel(offer))))) for offer in offers]
        journey_to_find.set_offers(offers)
        caption = str(offers[journey_to_find.current_offer])
        caption += f"\n {journey_to_find.current_offer + 1} out of {len(journey_to_find.offers)} offers"
        bot.send_photo(message.chat.id,
                       photo=open(offers[journey_to_find.current_offer].photo_path, "rb"),
                       caption=caption,
                       reply_markup=markup_generator.generate_markup_for_hotels())
    except Exception as e:
        msg = bot.reply_to(message, f'Oops, sorry, there is no journeys for current request. Try another one!')
        print(str(e))


# CALLBACK QUERIES
@bot.callback_query_handler(func=lambda call: call.data =='previous')
def show_previous_hotel(call):
    journey_to_find.current_offer = (journey_to_find.current_offer - 1) % len(journey_to_find.offers)
    bot.delete_message(
        call.message.chat.id,
        call.message.message_id
    )
    caption = str(journey_to_find.offers[journey_to_find.current_offer])
    caption += f"\n {journey_to_find.current_offer + 1} out of {len(journey_to_find.offers)} offers"
    bot.send_photo(call.message.chat.id,
                   photo=open(journey_to_find.offers[journey_to_find.current_offer].photo_path, "rb"),
                   caption=caption,
                   reply_markup=markup_generator.generate_markup_for_hotels())


@bot.callback_query_handler(func=lambda call: call.data =='next')
def show_next_hotel(call):
    journey_to_find.current_offer = (journey_to_find.current_offer + 1) % len(journey_to_find.offers)
    bot.delete_message(
        call.message.chat.id,
        call.message.message_id
    )
    caption = str(journey_to_find.offers[journey_to_find.current_offer])
    caption += f"\n {journey_to_find.current_offer + 1} out of {len(journey_to_find.offers)} offers"
    bot.send_photo(call.message.chat.id,
                   photo=open(journey_to_find.offers[journey_to_find.current_offer].photo_path, "rb"),
                   caption=caption,
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
    bot.clear_step_handler(call.message)
    bot.send_message(call.message.chat.id,
                     "Here is a list of all departure airports. Choose one(s) that you need!",
                     reply_markup=markup_generator.generate_markup_for_departure_airports(journey_to_find))


@bot.callback_query_handler(func=lambda call: call.data =='arrivalairports')
def show_arrival_airports(call):
    bot.clear_step_handler(call.message)
    bot.send_message(call.message.chat.id,
                     "Here is a list of all arrival airports. Choose one(s) that you need!",
                     reply_markup=markup_generator.generate_markup_for_arrival_airports(journey_to_find))


@bot.callback_query_handler(func=lambda call: call.data =='departure_ready')
def ready_with_departure_airports(call):
    msg = bot.reply_to(call.message, 'What is a *arrival airport*?',
                       parse_mode="Markdown",
                       reply_markup=markup_generator.generate_markup_from_word("List of airports", "arrivalairports"))
    bot.register_next_step_handler(msg, process_flight_to)


@bot.callback_query_handler(func=lambda call: call.data =='arrival_ready')
def ready_with_arrival_airports(call):
    msg = bot.reply_to(call.message, 'What is the *start date*? \n'
                                    'E.g. 29.09.2022', parse_mode="Markdown")
    bot.register_next_step_handler(msg, process_start_date)


@bot.callback_query_handler(func=lambda call: call.data =='all_offers')
def show_all_offers_for_hotel(call):
    raw_offers = asyncio.run(find_journey_for_hotel(journey_to_find))
    offers = [Offer(*list(raw_offer)) for raw_offer in raw_offers]
    offers = [offer.set_hotel(Hotel(*list(asyncio.run(find_hotel(offer))))) for offer in offers]
    journey_to_find.set_offers(offers)
    bot.send_photo(call.message.chat.id,
                   photo=open(offers[0].photo_path, "rb"),
                   caption=offers[0],
                   reply_markup=markup_generator.generate_markup_for_hotels())


@bot.callback_query_handler(func=lambda call: call.data.split('#')[0]=='dpage')
def characters_page_callback(call):
    print(call.data.split)
    page = int(call.data.split('#')[1])
    markup_generator.dpage = page
    bot.delete_message(
        call.message.chat.id,
        call.message.message_id
    )
    bot.send_message(call.message.chat.id,
                     "Here is a list of all departure airports. Choose one(s) that you need!",
                     reply_markup=markup_generator.generate_markup_for_departure_airports(journey_to_find, markup_generator.dpage))


@bot.callback_query_handler(func=lambda call: call.data.split('#')[0]=='apage')
def characters_page_callback(call):
    page = int(call.data.split('#')[1])
    markup_generator.apage = page
    bot.delete_message(
        call.message.chat.id,
        call.message.message_id
    )
    bot.send_message(call.message.chat.id,
                     "Here is a list of all arrival airports. Choose one(s) that you need!",
                     reply_markup=markup_generator.generate_markup_for_arrival_airports(journey_to_find, markup_generator.apage))


@bot.callback_query_handler(func=lambda call: call.data.split('#')[0] == 'd')
def change_departure_airport(call):
    print(call.data)
    airport_code = call.data[-4:-1]  # "Airport (PLZ)" -> "PLZ"
    if airport_code not in journey_to_find.flight_from:
        journey_to_find.add_airport_to_flight_from(airport_code)
    else:
        journey_to_find.delete_airport_to_flight_from(airport_code)
    new_markup = markup_generator.generate_markup_for_departure_airports(journey_to_find, markup_generator.dpage)
    bot.edit_message_text("Here is a list of all departure airports. Choose one(s) that you need!",
                          chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          reply_markup=new_markup)


@bot.callback_query_handler(func=lambda call: call.data.split('#')[0] == 'a')
def change_arrival_airport(call):
    print(call.data)
    airport_code = call.data[-4:-1]  # "Airport (PLZ)" -> "PLZ"
    if airport_code not in journey_to_find.flight_to:
        journey_to_find.flight_to.append(airport_code)
    else:
        journey_to_find.flight_to.remove(airport_code)
    new_markup = markup_generator.generate_markup_for_arrival_airports(journey_to_find, markup_generator.apage)
    bot.edit_message_text("Here is a list of all arrival airports. Choose one(s) that you need!",
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