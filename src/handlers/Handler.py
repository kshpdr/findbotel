from telebot import TeleBot
from telebot.types import CallbackQuery

import time
from utils.MarkupGenerator import MarkupGenerator
from utils.Database import Database
from models.Offer import Offer
from models.Hotel import Hotel
from models.SearchInfo import SearchInfo
from handlers.Processor import Processor

from telebot.types import LabeledPrice


prices = [LabeledPrice(label='Hotel Five Stars Riveera', amount=125050), LabeledPrice('Gift wrapping', 500)]


class Handler:
    users = {}
    # def __init__(self, journey_to_find: SearchInfo, database: Database, markup_generator: MarkupGenerator, processor: Processor):
    #     self.journey_to_find = journey_to_find
    #     self.database = database
    #     self.markup_generator = markup_generator
    #     self.processor = processor
    def __init__(self, database: Database, processor: Processor):
        self.database = database
        self.processor = processor

    def show_departure_airports(self, call: CallbackQuery, bot: TeleBot):
        user = self.users[call.from_user.id]
        bot.clear_step_handler(call.message)
        bot.send_message(call.message.chat.id,
                         "Here is a list of all departure airports. Choose one(s) that you need!",
                         reply_markup=user.markup_generator.generate_markup_for_departure_airports(user.journey_to_find))

    def show_arrival_airports(self, call: CallbackQuery, bot: TeleBot):
        user = self.users[call.from_user.id]
        bot.clear_step_handler(call.message)
        bot.send_message(call.message.chat.id,
                         "Here is a list of all arrival airports. Choose one(s) that you need!",
                         reply_markup=user.markup_generator.generate_markup_for_arrival_airports(user.journey_to_find))

    def ready_with_departure_airports(self, call: CallbackQuery, bot: TeleBot):
        user = self.users[call.from_user.id]
        msg = bot.reply_to(call.message, 'What is a *arrival airport*?',
                           parse_mode="Markdown",
                           reply_markup=user.markup_generator.generate_markup_from_word("List of airports", "arrivalairports"))
        bot.register_next_step_handler(msg, self.processor.process_flight_to)

    def ready_with_arrival_airports(self, call: CallbackQuery, bot: TeleBot):
        user = self.users[call.from_user.id]
        msg = bot.reply_to(call.message, 'What is the *start date*? \n'
                                        'E.g. 29.09.2022', parse_mode="Markdown")
        bot.register_next_step_handler(msg, self.processor.process_start_date)

    def show_all_offers_for_hotel(self, call: CallbackQuery, bot: TeleBot):
        user = self.users[call.from_user.id]
        raw_offers = self.database.find_journey_for_hotel(user.journey_to_find)
        offers = [Offer(*list(raw_offer[:17])).set_hotel(Hotel(*list(raw_offer[17:]))) for raw_offer in raw_offers]
        user.journey_to_find.set_offers(offers)
        caption = str(user.journey_to_find.offers[user.journey_to_find.current_offer])
        caption += f"\n {user.journey_to_find.current_offer + 1} out of {len(user.journey_to_find.offers)} offers"
        bot.send_photo(call.message.chat.id,
                       photo=open(user.journey_to_find.offers[user.journey_to_find.current_offer].photo_path, "rb"),
                       caption=caption,
                       reply_markup=user.markup_generator.generate_markup_for_hotels())

    def characters_dpage_callback(self, call: CallbackQuery, bot: TeleBot):
        user = self.users[call.from_user.id]
        print(call.data.split)
        page = int(call.data.split('#')[1])
        user.markup_generator.dpage = page
        bot.delete_message(
            call.message.chat.id,
            call.message.message_id
        )
        bot.send_message(call.message.chat.id,
                         "Here is a list of all departure airports. Choose one(s) that you need!",
                         reply_markup=user.markup_generator.generate_markup_for_departure_airports(user.journey_to_find, user.markup_generator.dpage))

    def characters_apage_callback(self, call: CallbackQuery, bot: TeleBot):
        user = self.users[call.from_user.id]
        page = int(call.data.split('#')[1])
        user.markup_generator.apage = page
        bot.delete_message(
            call.message.chat.id,
            call.message.message_id
        )
        bot.send_message(call.message.chat.id,
                         "Here is a list of all arrival airports. Choose one(s) that you need!",
                         reply_markup=user.markup_generator.generate_markup_for_arrival_airports(user.journey_to_find, user.markup_generator.apage))

    def change_departure_airport(self, call: CallbackQuery, bot: TeleBot):
        user = self.users[call.from_user.id]
        print(call.data)
        airport_code = call.data[-4:-1]  # "Airport (PLZ)" -> "PLZ"
        if airport_code not in user.journey_to_find.flight_from:
            user.journey_to_find.add_airport_to_flight_from(airport_code)
        else:
            user.journey_to_find.delete_airport_to_flight_from(airport_code)
        new_markup = user.markup_generator.generate_markup_for_departure_airports(user.journey_to_find, user.markup_generator.dpage)
        bot.edit_message_text("Here is a list of all departure airports. Choose one(s) that you need!",
                              chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              reply_markup=new_markup)

    def change_arrival_airport(self, call: CallbackQuery, bot: TeleBot):
        user = self.users[call.from_user.id]
        print(call.data)
        airport_code = call.data[-4:-1]  # "Airport (PLZ)" -> "PLZ"
        if airport_code not in user.journey_to_find.flight_to:
            user.journey_to_find.flight_to.append(airport_code)
        else:
            user.journey_to_find.flight_to.remove(airport_code)
        new_markup = user.markup_generator.generate_markup_for_arrival_airports(user.journey_to_find, user.markup_generator.apage)
        bot.edit_message_text("Here is a list of all arrival airports. Choose one(s) that you need!",
                              chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              reply_markup=new_markup)

    def show_previous_hotel(self, call: CallbackQuery, bot: TeleBot):
        user = self.users[call.from_user.id]
        user.journey_to_find.current_offer = (user.journey_to_find.current_offer - 1) % len(user.journey_to_find.offers)
        bot.delete_message(
            call.message.chat.id,
            call.message.message_id
        )
        caption = str(user.journey_to_find.offers[user.journey_to_find.current_offer])
        caption += f"\n {user.journey_to_find.current_offer + 1} out of {len(user.journey_to_find.offers)} offers"
        bot.send_photo(call.message.chat.id,
                       photo=open(user.journey_to_find.offers[user.journey_to_find.current_offer].photo_path, "rb"),
                       caption=caption,
                       reply_markup=user.markup_generator.generate_markup_for_hotels())

    def show_next_hotel(self, call: CallbackQuery, bot: TeleBot):
        user = self.users[call.from_user.id]
        user.journey_to_find.current_offer = (user.journey_to_find.current_offer + 1) % len(user.journey_to_find.offers)
        bot.delete_message(
            call.message.chat.id,
            call.message.message_id
        )
        caption = str(user.journey_to_find.offers[user.journey_to_find.current_offer])
        caption += f"\n {user.journey_to_find.current_offer + 1} out of {len(user.journey_to_find.offers)} offers"
        bot.send_photo(call.message.chat.id,
                       photo=open(user.journey_to_find.offers[user.journey_to_find.current_offer].photo_path, "rb"),
                       caption=caption,
                       reply_markup=user.markup_generator.generate_markup_for_hotels())

    def start_payment(self, call: CallbackQuery, bot: TeleBot):
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

    def send_location(self, call: CallbackQuery, bot: TeleBot):
        user = self.users[call.from_user.id]
        bot.send_location(call.message.chat.id,
                          latitude=user.journey_to_find.offers[user.journey_to_find.current_offer].hotel.latitude,
                          longitude=user.journey_to_find.offers[user.journey_to_find.current_offer].hotel.longitude)

