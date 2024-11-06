import re
from pathlib import Path
from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from crud_functions import *


api = "_"
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())

kb = ReplyKeyboardMarkup(resize_keyboard=True)
button1 = KeyboardButton(text='Рассчитать')
button2 = KeyboardButton(text='Информация')
button3 = KeyboardButton(text='Купить')
button4 = KeyboardButton(text='Регистрация')
kb.row(button1, button4)
kb.row(button3, button2)

inln_kb = InlineKeyboardMarkup(resize_keyboard=True)
inln_button1 = InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories')
inln_button2 = InlineKeyboardButton(text='Формулы расчёта', callback_data='formulas')
inln_kb.row(inln_button1, inln_button2)

inln_kb_pr = InlineKeyboardMarkup(resize_keyboard=True)
inln_kb_pr1 = InlineKeyboardButton(text='Product 1', callback_data='product_buying')
inln_kb_pr2 = InlineKeyboardButton(text='Product 2', callback_data='product_buying')
inln_kb_pr3 = InlineKeyboardButton(text='Product 3', callback_data='product_buying')
inln_kb_pr4 = InlineKeyboardButton(text='Product 4', callback_data='product_buying')
inln_kb_pr.row(inln_kb_pr1, inln_kb_pr2, inln_kb_pr3, inln_kb_pr4)


class RegistrationState(StatesGroup):
    username = State()
    email = State()
    age = State()
    balance = State()


@dp.message_handler(text='Регистрация')
async def sign_up(message):
    await message.answer("Введите имя пользователя (только латинский алфавит):")
    await RegistrationState.username.set()


@dp.message_handler(state=RegistrationState.username)
async def set_username(message, state):
    username = message.text.strip()
    if is_included(username):
        await message.answer("Пользователь существует, введите другое имя:")
    else:
        await state.update_data(username=username)
        await message.answer("Введите свой email:")
        await RegistrationState.email.set()


def is_valid_email(email):
    shablon = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(shablon, email) is not None


@dp.message_handler(state=RegistrationState.email)
async def set_email(message, state):
    email = message.text.strip()
    if not is_valid_email(email):
        await message.answer("Некорректный email. Пожалуйста, введите действительный email:")
    else:
        await state.update_data(email=email)
        await message.answer("Введите свой возраст:")
        await RegistrationState.age.set()


@dp.message_handler(state=RegistrationState.age)
async def set_age(message, state):
    if 110 >= int(message.text) >= 0:
        await state.update_data(age=message.text)
        user_data = await state.get_data()
        add_user(user_data['username'], user_data['email'], user_data['age'])
        await message.answer("Регистрация успешна!")
        await state.finish()
    else:
        await message.answer("Введите корректный возраст.")
        await RegistrationState.age.set()


class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()


@dp.message_handler(commands=['start'])
async def start(message):
    await message.answer('Привет! Я бот помогающий твоему здоровью.', reply_markup=kb)


@dp.message_handler(text='Рассчитать')
async def main_menu(message):
    await message.answer('Выберите опцию:', reply_markup=inln_kb)


@dp.callback_query_handler(text='formulas')
async def get_formulas(call):
    await call.message.answer('Упрощенный вариант формулы Миффлина-Сан Жеора для мужчин:\n'
                              '10 х вес (кг) + 6,25 x рост (см) – 5 х возраст (г) + 5')
    await call.answer()


@dp.callback_query_handler(text='calories')
async def set_age(call):
    await call.message.answer('Введите свой возраст:')
    await UserState.age.set()


@dp.message_handler(state=UserState.age)
async def set_growth(message, state):
    await state.update_data(age=message.text)
    await message.answer('Введите свой рост:')
    await UserState.growth.set()


@dp.message_handler(state=UserState.growth)
async def set_weight(message, state):
    await state.update_data(growth=message.text)
    await message.answer('Введите свой вес:')
    await UserState.weight.set()


@dp.message_handler(state=UserState.weight)
async def send_calories(message, state):
    await state.update_data(weight=message.text)
    data = await state.get_data()
    res = (10 * int(data['weight']) + 6.25 * int(data['growth']) - 5 * int(data['age']) + 5)
    await message.answer(f'Ваша норма калорий: {res}')
    await state.finish()


@dp.message_handler(text='Купить')
async def get_buying_list(message):
    products = get_all_products()
    image_dir = 'image_14_3'
    images = [f for f in Path(image_dir).iterdir() if f.is_file()]
    for i, product in enumerate(products, start=1):
        if i <= len(images):
            image = images[i - 1]
            with open(image, "rb") as f:
                await message.answer(f'Название: {product[1]} | Описание: {product[2]} | Цена: {product[3]}')
                await message.answer_photo(f)
    await message.answer('Выберите продукт для покупки:', reply_markup=inln_kb_pr)


@dp.callback_query_handler(text='product_buying')
async def send_confirm_message(call):
    await call.message.answer('Вы успешно приобрели продукт!')
    await call.answer()


@dp.message_handler(text='Информация')
async def info(massage):
    await massage.answer('Предполагаемая инфа о боте.', reply_markup=kb)


@dp.message_handler()
async def all_massages(message):
    await message.answer('Введите команду /start, чтобы начать общение.')


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
