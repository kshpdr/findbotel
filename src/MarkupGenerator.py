from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telegram_bot_pagination import InlineKeyboardPaginator


class MarkupGenerator:
    @staticmethod
    def generate_markup_from_word(word, callback_data):
        markup = InlineKeyboardMarkup()
        markup.row_width = 1
        markup.add(InlineKeyboardButton(word, callback_data=callback_data))
        return markup

    @staticmethod
    def generate_markup_from_list(list, callback_data):
        markup = InlineKeyboardMarkup()
        markup.row_width = 1
        for element in list:
            markup.add(InlineKeyboardButton(element, callback_data=callback_data))
        return markup

    def generate_markup_from_dict(self, dictionary, page=1, chosen=[]):
        total_pages = int(len(dictionary) / 10 + (len(dictionary) % 10 > 0))
        paginator = InlineKeyboardPaginator(
            page_count=total_pages,
            current_page=page,
            data_pattern="page#{page}"
        )

        dictionary = self.mark_as_chosen_in_dict(dictionary, chosen)
        array = self.transform_dict_into_list(dictionary)

        for i in range((page-1) * 10, (page-1) * 10 + (len(array) % 10)*(page == total_pages) + 10*(page != total_pages)):
            paginator.add_after(InlineKeyboardButton(f'{array[i]}', callback_data=f'{array[i]}'))

        paginator.add_after(InlineKeyboardButton("I am ready!", callback_data="ready"))

        return paginator.markup

    @staticmethod
    def transform_dict_into_list(dictionary):
        array = []
        for key in list(dictionary.keys()):
            array.append(f"{dictionary[key]} ({key})")
        return array

    @staticmethod
    def mark_as_chosen_in_dict(dictionary, chosen):
        for key in list(dictionary.keys()):
            if key in chosen:
                dictionary[key] = "✔️ " + dictionary[key]
                break
        print(f"CHECK DICK {dictionary}")
        return dictionary

    @staticmethod
    def add_airport_to_markup(markup, airport):
        new_markup_keyboard = markup.keyboard
        for i in range(len(new_markup_keyboard)):
            if len(new_markup_keyboard[i]) == 1 and new_markup_keyboard[i][0].text == airport:
                new_markup_keyboard[i][0] = InlineKeyboardButton(f"✔️ {airport}", callback_data=airport)
                break
        new_markup = InlineKeyboardMarkup(new_markup_keyboard)
        return new_markup

    @staticmethod
    def delete_airport_to_markup(markup, airport):
        new_markup_keyboard = markup.keyboard
        for i in range(len(new_markup_keyboard)):
            if len(new_markup_keyboard[i]) == 1 and airport in new_markup_keyboard[i][0].text:
                new_markup_keyboard[i][0] = InlineKeyboardButton(f"{airport}", callback_data=airport)
                break
        new_markup = InlineKeyboardMarkup(new_markup_keyboard)
        return new_markup
