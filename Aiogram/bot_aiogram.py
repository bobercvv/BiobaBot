# .ENV
import os # Для работы с .env
from dotenv import find_dotenv, load_dotenv # инструменты для работы с переменными окружения
load_dotenv(find_dotenv()) # получение всех данных из .env

# AIOGRAM
from aiogram import Bot, Dispatcher, types  # Импорт библиотеки aiogram
import asyncio # импорт библиотеки для работы с асинхронными функциями
from aiogram.enums import ParseMode # Выбор режима парса для отправляемых сообщений
from aiogram.fsm.strategy import FSMStrategy # Параметры в диспетчре для машины состояний FSM

# MODULES
from Handlers.users_handlers import user_p_R # Роутер обработки данных от пользователей
from Aiogram.Handlers.admin_handlers import admin_R
from Aiogram.Common.commands_list import private # Импорт комманд, отображаемых в меню клавиатуры
from Aiogram.Database.engine import create_db, drop_db, session_maker
from Aiogram.Middlewares.database_mw import DatabaseSession

# BOT & DISPATCHER
bot = Bot(token=os.getenv("TOKEN")) # Сам бот с токеном
dp = Dispatcher()


# ROUTERS
dp.include_router(user_p_R) # Подключение роутера для обчыных пользователей
dp.include_router(admin_R)

# ФУНКЦИИ ДЛЯ РАБОТЫ БД
async def on_startup(bot):
    run_param = False
    if run_param:
        await drop_db()
    await create_db()

async def on_shutdown(bot):
    print('бот лег')


# MAIN FUNCTION
async def main():
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    dp.update.middleware(DatabaseSession(session_pool=session_maker))

    await create_db() # Запуск БД
    await bot.delete_webhook(drop_pending_updates=True) # Скипает сообщения, которые приходили боту пока он был неактивен
    await bot.set_my_commands(commands=private, scope=types.BotCommandScopeAllPrivateChats())
    await dp.start_polling(bot) # Старт работы бота (можно указать параметр allowed_updates=[] для фильтрации необходимых событий)

print("Compilation complete.")
asyncio.run(main())



