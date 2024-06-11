import telebot
from currency_converter import CurrencyConverter # Библиотека для конвертации валют

bot = telebot.TeleBot('7112434036:AAH_OtIUf4MCNXAqXzjcRdBA4nra6UOAkTY') # Указание токена на бота

users = []

currency = CurrencyConverter()

# Теги HTML: <b><\b> - жирный шрифт, <em><\em> - курсивный шрифт, <u><\u> - шрифт с подчеркиванием,
# bot.reply_to(message, text) - ответ на сообщение


# @bot.message_handler(content_types=['photo']) # Здесь обрабатываются фотографии
# def photo_message(message):
#     markup = types.InlineKeyboardMarkup() # Создание объекта через который будем добавлять кнопки
#     # markup.add(types.InlineKeyboardButton("Перейти на сайт", url="http://bioba.ru/")) # Создание кнопки
#     # markup.add(types.InlineKeyboardButton("Удалить фото", callback_data='delete')) # callback_data - вызов функции, которая отвечает на переданную комманду
#     button1 = types.InlineKeyboardButton("Перейти на сайт", url="http://bioba.ru/")
#     button2 = types.InlineKeyboardButton("Удалить фото", callback_data='delete')
#     button3 = types.InlineKeyboardButton("Изменить фото", callback_data='edit')
#     markup.row(button1)
#     markup.row(button2,button3)
#     bot.reply_to(message, "Охуительная фотокарточка!", reply_markup=markup) # message.chat.id - получение id чата
#
# @bot.callback_query_handler(func=lambda callback: callback.data in ['delete','edit']) # Декоратор для обработки callback_data
# def callback_message(callback):
#     if callback.data == 'delete':
#         bot.delete_message(callback.message.chat.id, callback.message.message_id - 1) # message_id - 1 - удаление предпоследнего сообщения
#         bot.delete_message(callback.message.chat.id, callback.message.message_id)
#     elif callback.data == 'edit':
#         bot.edit_message_text("Edit text", callback.message.chat.id, callback.message.message_id)


print("Compilation complete.")
bot.polling(none_stop=True) # Строка не завершает процесс выполнения кода, а оставляет программу открытой
#bot.infinity_polling() # Аналогичная строка для постоянной работы бота