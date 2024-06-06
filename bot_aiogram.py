import os # Для работы с .env
# types - для настройки кнопок, Bot - для связи с API Telegram, Dispatcher - для обработки апдейтов из чата, filters - для обработки комманд хендлером
from aiogram import Bot, Dispatcher, types, filters # Библа aiogram
import currencies, users_database # Свои модули
import asyncio
from dotenv import find_dotenv, load_dotenv # инструменты для работы с переменнвыми окружения
load_dotenv(find_dotenv()) # получение всех данных из .env

# Сам бот с токеном
bot = Bot(token=os.getenv("TOKEN"))
# Dispatcher - класс, отвечающий за обработку сообщений, которые бот получает из тг
dp = Dispatcher()

@dp.message(filters.CommandStart()) # Декоратор для обработки start: filters.CommandStart
async def start_command(message: types.Message):
    await message.answer(f"Доброго здравия, {message.from_user.first_name}! С помощью общения со мной вы можете узнать курс валют и оформить заказ через Bioba.")
    users_database.register(message)

# @dp.message(commands=['menu'])
# async def menu_command(message: types.Message):
#     markup = types.InlineKeyboardMarkup(row_width=2)  # Создание объекта через который будем добавлять кнопки
#     button1 = types.InlineKeyboardButton('Перейти на сайт',callback_data="Перейти на сайт")
#     button2 = types.InlineKeyboardButton("Курсы валют", callback_data="Курсы валют")
#     button3 = types.InlineKeyboardButton("Рассчёт стоимости товара", callback_data="Рассчёт стоимости товара")
#     markup.add(button1,button2,button3)
#     file = open('./smile.jpg', 'rb') # 'rb' - открытие на чтение
#     await message.answer_photo(file) # отправление файла в чат
#     await message.answer("Вы перенаправлены в меню BiobaBot 😤", reply_markup=markup)


async def main():
    await bot.delete_webhook(drop_pending_updates=True) # Скипает сообщения, которые приходили боту пока он был неактивен
    await dp.start_polling(bot) # Старт работы бота
asyncio.run(main())
