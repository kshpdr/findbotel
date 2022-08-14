import local_config as config
import telebot
from flask import Flask, request
import os
import logging
from SearchInfo import SearchInfo

bot = telebot.TeleBot(config.telegram_token)

@bot.message_handler(commands=['start'])
def start_command(message):
    msg = bot.reply_to(message, "Let's start new search! First of all, type the "
                                "name of the city where you want to start your journey")
    bot.register_next_step_handler(msg, process_flight_from)

def process_flight_from(message):
    try:
        chat_id = message.chat.id
        flight_from = message.text


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