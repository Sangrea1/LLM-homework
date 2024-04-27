from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import config
from aiogram.dispatcher.filters.state import StatesGroup, State
import requests


class States(StatesGroup):
    """
        Класс стейтов чат - бота
    """
    start = State()
    help = State()
    section_choice = State()
    address_choice = State()


class MakeKeyboard:
    """
        Класс создания клавиатур
    """
    @staticmethod
    def reply(list_button: list) -> types.ReplyKeyboardMarkup:
        """
        5.2.2 Функция для создания reply - клавиатуры

        @param list_button: Лист для создания клавиатуры (одно значение из листа - одна кнопка)

        @return: Экземпляр reply - клавиатуры
        """
        keyboard_variants = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        for i in list_button:
            keyboard_variants.add(types.KeyboardButton(i))
        return keyboard_variants

    @staticmethod
    def inline(button_list: list, width: int = 1) -> types.InlineKeyboardMarkup:
        """
        5.2.3 Функция для создания inline - клавиатуры

        @param button_list: Лист для создания клавиатуры (одно значение из листа - одна кнопка)
        @param width: Ширина inline - клавиатуры (default value = 1), если хотим расширить то пишем 2

        @return: Экземпляр inline - клавиатуры
        """
        first_stage_markup = InlineKeyboardMarkup(row_width=width)
        InlineKeyboardMarkup()
        for idx, x in enumerate(button_list):
            first_stage_markup.insert(InlineKeyboardButton(text=x, callback_data=x[:32]))
        return first_stage_markup

class GetData:
    """
        Класс получения данных по API apidata.mos.ru
    """
    @staticmethod
    def apidata_response(number: str, number_type: str) -> [list, list]:
        """
        Функция запроса по API apidata.mos.ru

        :param number: Номер по которому ищем информацию
        :param number_type: Поле для сравнения поиска

        :return: Возвращаем лист адресов и лист с информацией ао каждому адресу
        """
        url = config.apidata_url.format(number)
        r = requests.get(url=url, timeout=30)
        addreses = []
        addreses_info = []
        for data in r.json():
            if data['Cells'][number_type][0][number_type] == number:
                addreses.append(data['Cells']['SIMPLE_ADDRESS'])
                addreses_info.append(data['Cells'])
        return addreses, addreses_info

if __name__ == '__main__':

    GetData.apidata_response("77:09:0004023:11111111111111111", 'KAD_N')