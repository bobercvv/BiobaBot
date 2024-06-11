import os # Для работы с .env
from dotenv import find_dotenv, load_dotenv # инструменты для работы с переменнвыми окружения
load_dotenv(find_dotenv()) # получение всех данных из .env

import telebot
import webbrowser # Для перенаправления на сайт
from telebot import types # Для добавления кнопок под сообщениями
import re # Работа с регулярными выражениями

from currency_converter import CurrencyConverter # Библиотека для конвертации валют
import users_database, currencies

bot = telebot.TeleBot(token=os.getenv("TOKEN")) # Указание токена на бота

currency = CurrencyConverter()

# Теги HTML: <b><\b> - жирный шрифт, <em><\em> - курсивный шрифт, <u><\u> - шрифт с подчеркиванием,
# bot.reply_to(message, text) - ответ на сообщение
# bot.send_message(message, text) - отправление сообщения в чат

@bot.message_handler(commands=['start']) # Декоратор для обработки сообщений. Здесь обрабатывается комманда /start
def start_command(message):
    bot.send_message(message.chat.id, f"Доброго здравия, {message.from_user.first_name}! С помощью общения со мной вы можете узнать курс валют и оформить заказ через Bioba.") # message.chat.id - получение id чата
    users_database.register(message)

@bot.message_handler(commands=['menu'])
def menu_command(message):
    markup = types.InlineKeyboardMarkup(row_width=2)  # Создание объекта через который будем добавлять кнопки
    button1 = types.InlineKeyboardButton("Перейти на сайт",callback_data="Перейти на сайт")
    button2 = types.InlineKeyboardButton("Курсы валют", callback_data="Курсы валют")
    button3 = types.InlineKeyboardButton("Рассчёт стоимости товара", callback_data="Рассчёт стоимости товара")
    markup.add(button1,button2,button3)
    file = open('../smile.jpg', 'rb') # 'rb' - открытие на чтение
    bot.send_photo(message.chat.id, file) # отправление файла в чат
    bot.send_message(message.chat.id, "Вы перенаправлены в меню BiobaBot 😤", reply_markup=markup)

@bot.callback_query_handler(lambda call: call.data in ["Перейти на сайт","Курсы валют","Рассчёт стоимости товара"])
def on_click(call):
    if call.data == 'Перейти на сайт':
        site_command(call.message)
    elif call.data == 'Курсы валют':
        currency_message(call.message)
    elif call.data == 'Рассчёт стоимости товара':
        bot.send_message(call.message.chat.id, "Введите стоимость товара в CNY")
        bot.register_next_step_handler(call.message, product_cost_message)
    else:
        bot.send_message(call.message.chat.id, "Неправильно!")

@bot.message_handler(commands=['site'])
def site_command(message): # Перенаправление на сайт Bioba
    bot.send_message(message.chat.id, 'Открывается сайт Bioba')
    webbrowser.open('http://bioba.ru/')


@bot.message_handler(commands=['currency'])
def currency_message(message): # Ввод информации о нужной паре валют
    markup = types.InlineKeyboardMarkup(row_width=3)
    button1 = types.InlineKeyboardButton("CNY/RUB", callback_data="CNY/RUB")
    button2 = types.InlineKeyboardButton("USD/RUB", callback_data='USD/RUB')
    button3 = types.InlineKeyboardButton("USD/CNY", callback_data='USD/CNY')
    button4 = types.InlineKeyboardButton("Другая пара валют", callback_data='other')
    markup.add(button1,button2,button3,button4)
    bot.send_message(message.chat.id, "Выберите пару валют, для которых хотите узнать курс", reply_markup=markup)

@bot.callback_query_handler(lambda call: call.data in ['other',"CNY/RUB",'USD/RUB','USD/CNY'])
def ratio_currency(call): # Метод рассчета пары валют CNY/RUB, USD/RUB, USD/CNY
    if call.data != "other":
        values = call.data.split('/')
        if values[1] == "RUB":
            bot.send_message(call.message.chat.id, f"Сейчас курс {values[0]}/RUB равен: {currencies.TO_RUB(values[0])}")
        else:
            res = round(currency.convert(1, values[0], values[1]), 2)
            bot.send_message(call.message.chat.id, f"Сейчас курс {values[0]}/{values[1]} равен: {res}")
    else:
        bot.send_message(call.message.chat.id, "Чтобы узнать курс валют, введите пару в формате: ВАЛЮТА_1/ВАЛЮТА_2")
        bot.register_next_step_handler(call.message, other_currency)

def other_currency(message): # Метод рассчета пары валют, введённых пользователем
    if re.match(r"^[A-Za-z]{3}/[A-Za-z]{3}$", message.text.strip()):
        values = message.text.upper().split('/')
        if values[1] == "RUB":
            bot.send_message(message.chat.id, f"Сейчас курс {values[0]}/RUB равен: {currencies.TO_RUB(values[0])}")
        else:
            res = round(currency.convert(1, values[0], values[1]), 2)
            bot.send_message(message.chat.id, f"Сейчас курс {values[0]}/{values[1]} равен: {res}")
    else:
        bot.send_message(message.chat.id, f"Вы ввели неверное сообщение. Повторите ввод.")
        bot.register_next_step_handler(message, other_currency)


def product_cost_message(message): # Метод рассчета стоимоти товара
    amount = message.text
    try:
        amount = float(message.text.strip())
    except Exception:
        bot.send_message(message.chat.id, "Некорректные данные. Введите корректную стоимость в CNY.")
        bot.register_next_step_handler(message, product_cost_message)
        return

    if amount > 0:
        bot.send_message(message.chat.id, f"Рассчётная стоимость товара составляет: {round(float(currencies.TO_RUB('CNY')) * amount, 2)} рублей")
    else:
        bot.send_message(message.chat.id, "Введено неверное значение. Пришлите корректную стоимость в CNY.")
        bot.register_next_step_handler(message, product_cost_message)


# @bot.message_handler(commands=['pay'])
# def pay_command(message):
#     bot.send_invoice(message.chat.id, "Оплата заказа", "Наименование товара с площадки Poizon", 'invoice', payment_token, "RUB", [types.LabeledPrice('Наименование товара с площадки Poizon', 1000 * 100)])
#
# @bot.message_handler(content_types=types.InputInvoiceMessageContent())
#




@bot.message_handler(commands=['help']) # Здесь обрабатывается комманда /help
def help_command(message):
    bot.send_message(message.chat.id, f"""<b>ИНФОРМАЦИЯ ДЛЯ РАБОТЫ С БОТОМ</b>\n
Список доступных комманд:
/start - Старт бота
/menu - Комманда вызова меню бота
/currency - Узнать курсы валют
/site - Открытие сайта Bioba
/chat_info - Информация о чате
/help - Информация для работы с ботом""", parse_mode='html') # message.chat.id - получение id чата

@bot.message_handler(commands=['chat_info']) # Здесь обрабатывается комманда /chat_info
def chatInfo_command(message):
    bot.send_message(message.chat.id, message) # message.chat.id - получение id чата



@bot.message_handler() # Обработка любых сообщений
def random_message(message):
    if message.text.lower() == 'инфа':
        send = f'Никнейм: {message.from_user.first_name}\nЮзернейм: {message.from_user.username}\nПремиум: ' + "есть" if message.from_user.is_premium else "Нет"
        bot.send_message(message.chat.id, send)
    elif message.text == 'Перейти на сайт':
        site_command(message)
    elif message.text == 'Курс валют':
        return currency_message(message)
    elif message.text == 'Рассчёт стоимости товара':
        bot.send_message(message.chat.id, "Введите стоимость товара в CNY")
        bot.register_next_step_handler(message, product_cost_message)

print("Compilation complete.")
bot.polling(none_stop=True) # Строка не завершает процесс выполнения кода, а оставляет программу открытой
#bot.infinity_polling() # Аналогичная строка для постоянной работы бота