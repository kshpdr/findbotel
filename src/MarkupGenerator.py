from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telegram_bot_pagination import InlineKeyboardPaginator

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

    def generate_markup_from_dict(self, dictionary, page=1):
        total_pages = int(len(dictionary) / 10 + (len(dictionary) % 10 > 0))
        paginator = InlineKeyboardPaginator(
            page_count=total_pages,
            current_page=page,
            data_pattern="page#{page}"
        )

        array = self.transform_dict_into_list(dictionary)

        for i in range((page-1) * 10, (page-1) * 10 + (len(array) % 10)*(page == total_pages) + 10*(page != total_pages)):
            paginator.add_after(InlineKeyboardButton(f'{array[i]}', callback_data=i))

        return paginator.markup

    def transform_dict_into_list(self, dictionary):
        array = []
        for key in list(dictionary.keys()):
            array.append(f"{dictionary[key]} ({key})")
        return array
