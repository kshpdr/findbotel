#import local_config as config
import env_config as config

import telebot
import os
import logging
from flask import Flask, request

from handlers.Handler import Handler
from handlers.Processor import Processor
from utils.Database import Database
from utils.MarkupGenerator import MarkupGenerator
from models.SearchInfo import SearchInfo
from models.User import User

bot = telebot.TeleBot(config.telegram_token)
database = Database(config.DATABASE_URL)
users = {}


processor = Processor(bot, database)
handler = Handler(database, processor)


@bot.message_handler(commands=['start'])
def start_command(message):
    users[message.from_user.id] = User(message.from_user.id, SearchInfo(), MarkupGenerator())
    processor.users = users
    handler.users = users
    print(users)

    msg = bot.reply_to(message, "Let's start new search! Simply type your answer, "
                                "by multiple options just separate them with commas, "
                                "or choose ones from the list. \n \n"
                                "What is a *departure airport(s)*? \n"
                                "e.g. 'Berlin,Frankfurt'",
                       parse_mode="Markdown",
                       reply_markup=users[message.from_user.id].markup_generator.generate_markup_from_word("List of airports", "departureairports"))
    bot.register_next_step_handler(msg, processor.process_flight_from)


def register_handlers():
    bot.register_callback_query_handler(handler.show_departure_airports, lambda call: call.data =='departureairports', pass_bot=True)
    bot.register_callback_query_handler(handler.show_arrival_airports, lambda call: call.data == 'arrivalairports', pass_bot=True)
    bot.register_callback_query_handler(handler.ready_with_departure_airports, lambda call: call.data == 'departure_ready', pass_bot=True)
    bot.register_callback_query_handler(handler.ready_with_arrival_airports, lambda call: call.data == 'arrival_ready', pass_bot=True)
    bot.register_callback_query_handler(handler.characters_dpage_callback, lambda call: call.data.split('#')[0]=='dpage', pass_bot=True)
    bot.register_callback_query_handler(handler.characters_apage_callback, lambda call: call.data.split('#')[0]=='apage', pass_bot=True)
    bot.register_callback_query_handler(handler.change_departure_airport, lambda call: call.data.split('#')[0] == 'd', pass_bot=True)
    bot.register_callback_query_handler(handler.change_arrival_airport, lambda call: call.data.split('#')[0] == 'a', pass_bot=True)
    bot.register_callback_query_handler(handler.show_previous_hotel, lambda call: call.data =='previous', pass_bot=True)
    bot.register_callback_query_handler(handler.show_next_hotel, lambda call: call.data =='next', pass_bot=True)
    bot.register_callback_query_handler(handler.start_payment, lambda call: call.data == 'pay', pass_bot=True)
    bot.register_callback_query_handler(handler.send_location, lambda call: call.data == 'maps', pass_bot=True)
    bot.register_callback_query_handler(handler.show_all_offers_for_hotel, lambda call: call.data == 'all_offers', pass_bot=True)


register_handlers()

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