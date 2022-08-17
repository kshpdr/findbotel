import local_config as config
import telebot
from flask import Flask, request
import os
import logging
import datetime
from SearchInfo import SearchInfo
from Database import Database
from MarkupGenerator import MarkupGenerator
from unique_data import *

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


def process_flight_from(message):
    flight_from = message.text.split(",")
    #print(database.find_unique_flight_from())
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
    # print(database.find_unique_flight_from())
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
    # print(database.find_unique_flight_from())
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
    # print(database.find_unique_flight_from())
    try:
        journey_to_find.set_end_date(end_date)
        msg = bot.reply_to(message, 'How many adults are going? E.g. 2', parse_mode="Markdown")
        bot.register_next_step_handler(msg, process_persons)
    except Exception as e:
        msg = bot.reply_to(message, f'Oops, date was sent in a wrong format. Try again!')
        bot.register_next_step_handler(msg, process_end_date)


def process_persons(message):
    persons = message.text
    journey_to_find.persons(persons)
    msg = bot.reply_to(message, 'How many children are going? E.g. 1')
    bot.register_next_step_handler(msg, process_kids)


def process_kids(message):
    kids = message.text
    journey_to_find.kids(kids)
    msg = bot.reply_to(message, 'Thanks! We are searching for a best journey for you...')
    print(journey_to_find)


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