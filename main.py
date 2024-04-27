from aiogram import Bot, Dispatcher,executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher import FSMContext
import config
from functions import MakeKeyboard, States, GetData
import dotenv
import regex

dotenv.load_dotenv()

bot = Bot(config.BOT_TOKEN)


storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


"""
Команды /start, /help 
"""


@dp.message_handler(commands='start', state='*')
async def start(message: Message):
    """
        1.1 Обработчик команды /start
    """
    answer = config.start['msg_start']
    keyboard = MakeKeyboard.reply(config.start['reply'])
    await message.answer(answer, reply_markup=keyboard)
    await States.start.set()
    await start_message(message)


@dp.message_handler(text=config.start['reply'][0], state='*')
@dp.message_handler(text=config.start['reply'][1], state='*')
async def start_message(message: Message):
    """
        1.2 Обработчик кнопок:
        ['В меню', 'Попробовать снова']
    """
    answer = config.start['msg']
    keyboard = MakeKeyboard.inline(config.start['buttons'])
    await message.answer(answer, reply_markup=keyboard)
    await States.start.set()


@dp.message_handler(commands='help', state='*')
async def start(message: Message):
    """
        1.3 Обработчик команды /help
    """
    answer = config.help['msg']
    keyboard = None
    await message.answer(answer, reply_markup=keyboard)
    await States.help.set()


@dp.callback_query_handler(state=States.start)
async def section_choice(call: CallbackQuery, state: FSMContext):
    """
        1.4 Обработчик команды инлайн - кнопок:
        ['Поиск по Кадастровому номеру', 'Поиск по номеру Земельного участка']
    """
    if config.start['buttons'][0].__contains__(call.data):
        answer = config.section_choice['msg_kn']
        action = 'KAD_N'
    else:
        answer = config.section_choice['msg_zu']
        action = 'KAD_ZU'
    async with state.proxy() as data:
        data['action'] = action
    keyboard = None
    await call.message.edit_text(answer, reply_markup=keyboard)
    await States.section_choice.set()


@dp.message_handler(content_types=['text'], state=States.section_choice)
async def address_choice(message: Message, state: FSMContext):
    """
        1.5 Обработчик сообщения пользователя с номером
    """
    async with state.proxy() as data:
        action = data['action']
        address_list, address_info_list = GetData.apidata_response(message.text, action)
        # Проверяем корректно ли был введен номер
        if regex.match(config.regex_num, message.text) == None:
            answer = config.address_choice['retry']
            keyboard = None
            state = States.section_choice.set()
        # Проверяем наличие информации об объекте
        elif address_list:
            keyboard = MakeKeyboard.inline(address_list)
            answer = config.address_choice['msg_found']
            data['address_info'] = address_info_list
            state = States.address_choice.set()
        # Если информации нет
        else:
            keyboard = None
            answer = config.address_choice['msg_not_found']
            state = States.start.set()
    await state
    await message.answer(answer, reply_markup=keyboard)


@dp.callback_query_handler(state=States.address_choice)
async def address_info(call: CallbackQuery, state: FSMContext):
    """
        1.6 Обработчик выбранного адреса, выводит информацию об объекте
    """
    async with state.proxy() as data:
        address_info = data['address_info']
    info = dict(
        address=address_info[0]['ADDRESS'],
        in_moscow=address_info[0]['OnTerritoryOfMoscow'],
        status=address_info[0]['STATUS']
    )
    # Форматируем ответ
    answer = config.address_info['msg'].format(**dict(info))
    keyboard = None
    coordinates = address_info[0]['geoData']['coordinates'][0][0]
    await call.message.edit_text(answer, reply_markup=keyboard)
    await bot.send_location(call['from'].id, coordinates[1], coordinates[0])
    await States.start.set()



executor.start_polling(dp, skip_updates=False)