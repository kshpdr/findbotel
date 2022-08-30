from telebot.types import Message
from telebot import TeleBot
import time

from utils.MarkupGenerator import MarkupGenerator
from utils.Database import Database
from models.Offer import Offer
from models.Hotel import Hotel
from models.SearchInfo import SearchInfo

class Processor:
    def __init__(self, bot: TeleBot, journey_to_find: SearchInfo, database: Database, markup_generator: MarkupGenerator):
        self.bot = bot
        self.journey_to_find = journey_to_find
        self.database = database
        self.markup_generator = markup_generator

    def start_command(self, message: Message):
        msg = self.bot.reply_to(message, "Let's start new search! Simply type your answer, "
                                    "by multiple options just separate them with commas, "
                                    "or choose ones from the list. \n \n"
                                    "What is a *departure airport(s)*? \n"
                                    "e.g. 'Berlin,Frankfurt'",
                           parse_mode="Markdown",
                           reply_markup=self.markup_generator.generate_markup_from_word("List of airports",
                                                                                   "departureairports"))
        self.bot.register_next_step_handler(msg, self.process_flight_from)

    def process_flight_from(self, message: Message):
        flight_from = message.text.split(",")
        try:
            self.journey_to_find.set_flight_from(flight_from)
            msg = self.bot.reply_to(message, 'What is a *arrival airport*?',
                               parse_mode="Markdown",
                               reply_markup=self.markup_generator.generate_markup_from_word("List of airports",
                                                                                       "arrivalairports"))
            self.bot.register_next_step_handler(msg, self.process_flight_to)
        except Exception as e:
            msg = self.bot.reply_to(message, f'Oops, there is no airport with name(s) {str(e)}. Try again!')
            self.bot.register_next_step_handler(msg, self.process_flight_from)

    def process_flight_to(self, message: Message):
        flight_to = message.text.split(",")
        print(self.journey_to_find.flight_from)
        try:
            self.journey_to_find.set_flight_to(flight_to)
            msg = self.bot.reply_to(message, 'What is the *start date*? \n'
                                        'E.g. 29.09.2022', parse_mode="Markdown")
            self.bot.register_next_step_handler(msg, self.process_start_date)
        except Exception as e:
            msg = self.bot.reply_to(message, f'Oops, there is no airport with name(s) {str(e)}. Try again!')
            self.bot.register_next_step_handler(msg, self.process_flight_to)

    def process_start_date(self, message: Message):
        start_date = message.text.split(".")
        try:
            self.journey_to_find.set_start_date(start_date)
            msg = self.bot.reply_to(message, 'What is the *end date*? \n'
                                        'E.g. 13.10.2022', parse_mode="Markdown")
            self.bot.register_next_step_handler(msg, self.process_end_date)
        except Exception as e:
            msg = self.bot.reply_to(message, f'Oops, date was sent in a wrong format. Try again!')
            self.bot.register_next_step_handler(msg, self.process_start_date)

    def process_end_date(self, message: Message):
        end_date = message.text.split(".")
        try:
            self.journey_to_find.set_end_date(end_date)
            msg = self.bot.reply_to(message, 'How many adults are going? E.g. 2', parse_mode="Markdown")
            self.bot.register_next_step_handler(msg, self.process_adults)
        except Exception as e:
            msg = self.bot.reply_to(message, str(e))
            self.bot.register_next_step_handler(msg, self.process_end_date)

    # TODO: add simple int checks
    def process_adults(self, message: Message):
        try:
            adults = message.text
            self.journey_to_find.set_adults(adults)
            msg = self.bot.reply_to(message, 'How many children are going? E.g. 1')
            self.bot.register_next_step_handler(msg, self.process_kids)
        except Exception as e:
            msg = self.bot.reply_to(message, str(e))
            self.bot.register_next_step_handler(msg, self.process_adults)

    def process_kids(self, message: Message):
        try:
            kids = message.text
            self.journey_to_find.set_kids(kids)
            msg = self.bot.reply_to(message, 'Thanks! We are searching for a best journey for you...')
            self.make_search(msg)
        except Exception as e:
            msg = self.bot.reply_to(message, str(e))
            self.bot.register_next_step_handler(msg, self.process_kids)

    def make_search(self, message: Message):
        try:
            start = time.time()
            print(f"started at {start}")
            #raw_offers = asyncio.run(find_journey(journey_to_find))
            raw_offers = self.database.find_journey(self.journey_to_find)
            finish = time.time()
            print(f"finished at {finish}")
            print(finish - start)
            offers = [Offer(*list(raw_offer)) for raw_offer in raw_offers]
            #offers = [offer.set_hotel(Hotel(*list(asyncio.run(find_hotel(offer))))) for offer in offers]
            offers = [offer.set_hotel(Hotel(*list(self.database.find_hotel(offer)))) for offer in offers]
            self.journey_to_find.set_offers(offers)
            caption = str(offers[self.journey_to_find.current_offer])
            caption += f"\n {self.journey_to_find.current_offer + 1} out of {len(self.journey_to_find.offers)} offers"
            self.bot.send_photo(message.chat.id,
                           photo=open(offers[self.journey_to_find.current_offer].photo_path, "rb"),
                           caption=caption,
                           reply_markup=self.markup_generator.generate_markup_for_hotels())
        except Exception as e:
            msg = self.bot.reply_to(message, f'Oops, sorry, there is no journeys for current request. Try another one!')
            print(str(e))