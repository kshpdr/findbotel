from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


class MarkupGenerator:
    def generate_markup_from_word(self, word, callback_data):
        markup = InlineKeyboardMarkup()
        markup.row_width = 1
        markup.add(InlineKeyboardButton(word, callback_data=callback_data))
        return markup

    def generate_markup_from_list(self, list, callback_data):
        markup = InlineKeyboardMarkup()
        markup.row_width = 1
        for element in list:
            markup.add(InlineKeyboardButton(element, callback_data=callback_data))
        return markup