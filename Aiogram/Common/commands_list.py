from aiogram.types import BotCommand

# start - Старт бота
# menu - Меню бота
# currency - Курсы валют
# site - Открытие сайта Bioba
# chat_info - Информация о чате
# help - Информация для работы с ботом
private = [
    BotCommand(command='start', description='Старт бота'),
    BotCommand(command='menu', description='Меню бота'),
    BotCommand(command='cart', description='Ваша корзина'),
    BotCommand(command='currency', description='Расчёт стоимости товара'),
    BotCommand(command='site', description='Открытие сайта Bioba'),
    BotCommand(command='delivery', description='Узнать, с каких площадок мы можем доставить товар'),
    BotCommand(command='contacts', description='Наши контакты'),
]

# BotCommand(command='chat_info', description='Информация о чате'),
# BotCommand(command='help', description='Информация для работы с ботом'),

