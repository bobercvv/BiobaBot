from aiogram.enums import ParseMode # Выбор режима парса для отправляемых сообщений
from aiogram.fsm.strategy import FSMStrategy # Параметры в диспетчре для машины состояний FSM

# .ENV
import os # Для работы с .env
from dotenv import find_dotenv, load_dotenv # инструменты для работы с переменными окружения
load_dotenv(find_dotenv()) # получение всех данных из .env
# AIOGRAM
from aiogram import Bot, Dispatcher, types  # Импорт библиотеки aiogram
import asyncio # импорт библиотеки для работы с асинхронными функциями
# MODULES
from Handlers.users_handlers import user_p_R # Роутер обработки данных от пользователей
from Aiogram.Handlers.admin_handlers import admin_R
from Aiogram.Common.commands_list import private # Импорт комманд, отображаемых в меню клавиатуры

# BOT & DISPATCHER
bot = Bot(token=os.getenv("TOKEN")) # Сам бот с токеном
dp = Dispatcher()
bot.my_admins_list = []
# ROUTERS
dp.include_router(user_p_R) # Подключение роутера для обчыных пользователей
dp.include_router(admin_R)


# MAIN FUNCTION
async def main():
    await bot.delete_webhook(drop_pending_updates=True) # Скипает сообщения, которые приходили боту пока он был неактивен
    await bot.set_my_commands(commands=private, scope=types.BotCommandScopeAllPrivateChats())
    await dp.start_polling(bot) # Старт работы бота (можно указать параметр allowed_updates=[] для фильтрации необходимых событий)

print("Compilation complete.")
asyncio.run(main())



