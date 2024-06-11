from aiogram import types, Router, F  # Библиотека aiogram
from aiogram.enums import ParseMode # Указывание Parse Mode для сообщений (Markdown/HTML)
from aiogram.filters import Command, or_f, StateFilter
from aiogram.fsm import state
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.formatting import Bold, as_list, as_marked_list, as_marked_section  # Функции для форматирования текста

import webbrowser # Работа с браузером для перенаправления на сайт

from Aiogram.Common.filters import IsNum
from Aiogram.Common.reply_keyboards import start_kbd, del_kbd, menu_kbd
from Aiogram.Modules import currencies



# ROUTER
user_p_R = Router() # user_private_router - роутер для работы с обработчиками комманд для обычных пользователей



# ОТМЕНА И СБРОС ВВОДА
# Сброс ввода
@user_p_R.message(StateFilter('*'), or_f(Command('cancel'), F.text.casefold() == 'отмена',F.text.casefold() == 'cancel'))
async def cancel(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.clear()

    await message.answer("Вы перенаправлены в меню бота", reply_markup=menu_kbd)

# Комманда назад
@user_p_R.message(StateFilter('*'), or_f(Command('back'), F.text.casefold() == 'назад', F.text.casefold() == 'back'))
async def back(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()

    if str(current_state) == "GetCurrency:value":
        await message.answer("Предыдущего шага нет, для отмены ввода нажмите /cancel")
        return

    previous_step = None
    for step in GetCurrency.__all_states__:
        if step.state == current_state:
            await state.set_state(previous_step)
            await message.answer(f"<i>Вы вернулись в прошлому шагу</i>: \n\n{GetCurrency.texts[previous_step.state]}", parse_mode=ParseMode.HTML)
            return
        previous_step = step



# Расчёт стоимости товара & /currency
class GetCurrency(StatesGroup):
    value = State()
    texts = {
        "SetCurrency:value": "Введите стоимость товара в CNY\n"
                             "(для выхода нажмите /cancel)"
    }

@user_p_R.message(StateFilter(None), or_f(Command("currency"), F.text.casefold() == 'расчёт стоимости товара'))
async def currency_command(message: types.Message, state: FSMContext):
    await message.answer("Введите стоимость товара в CNY\n(для перехода в меню нажмите /cancel)", reply_markup=del_kbd)
    await state.set_state(GetCurrency.value)

@user_p_R.message(GetCurrency.value, IsNum())
async def currency_command(message: types.Message, state: FSMContext):
    await state.update_data(value=float(message.text))
    data = await state.get_data()
    await message.answer(f"Расчётная стоимость товара составляет: {round(float(currencies.TO_RUB('CNY')) * data['value'], 2)}")
    await state.clear()

@user_p_R.message(GetCurrency.value)
async def currency_command(message: types.Message):
    await message.answer("Введены некорректные данные. Повторите ввод")



# START
@user_p_R.message(Command('start')) # Декоратор для обработки start: filters.CommandStart
async def start_command(message: types.Message):
    await message.answer(f"Доброго здравия, {message.from_user.first_name}! С помощью общения со мной вы можете оформить заказ через Bioba."
                         f"\n<b>Вот список доступных комманд:</b>"
                         f"\n/menu - доступ к меню бота"
                         f"\n/currency - расчёт стоимости товара"
                         f"\n/site - перенаправление на наш cайт Bioba"
                         f"\n/contacts - вы можете написать нам лично для оформления заказа"
                         f"\n/delivery - узнать, с каких площадок мы можем доставить вам товар", reply_markup=start_kbd, parse_mode=ParseMode.HTML)
    # users_database.register(message)



# MENU
@user_p_R.message(or_f(Command("menu"), F.text.lower() == "меню"))
async def menu_command(message: types.Message):
    await message.answer_photo(photo='AgACAgIAAxkBAAIDjmZmJuMvfJkQN-JiPQ_sNWMml_5BAAIo2jEbxbYxSzyH8_tpxSHfAQADAgADeAADNQQ')  # отправление файла в чат
    await message.answer("Вы перенаправлены в меню BiobaBot 😤.\n"
                         "Здесь Вы можете рассчитать примерную стоимость товара с учетом доставки.\n"
                         "Для оформеления заказа напишите нам в личные сообщения: /contacts", reply_markup=menu_kbd)



# SITE
@user_p_R.message(or_f(Command("site"), F.text.lower() == "сайт", F.text.lower() == "перейти на сайт"))
async def site_command(message): # Перенаправление на сайт Bioba
    await message.answer('Открывается сайт Bioba', reply_markup=del_kbd)
    webbrowser.open('http://bioba.ru/')



# CONTACTS
@user_p_R.message(Command("contacts"))
async def contacts_command(message):
    await message.answer("Для оформления заказа напишите сюда: \n@husbullik", reply_markup=del_kbd)



# DELIVERY
@user_p_R.message(or_f(Command("delivery"), F.text.lower().contains('доставк')))
async def delivery_command(message):
    text = as_marked_section(
        Bold("С каких площадок мы можем доставить товар:"),
        "TaoBao",
        "1688",
        "Poison",
        marker="✅ "
    )
    await message.answer(text.as_html(), reply_markup=del_kbd, parse_mode=ParseMode.HTML)








@user_p_R.message(F.photo)
async def menu_command(message: types.Message):
    await message.answer(str(message.photo[-1]))  # отправление файла в чат



# @user_p_R.message(F.text.lower().contains('хуесос'))
# async def start_command(message: types.Message):
#     await message.reply("Пошёл в жопу, кусок говна")
#
# @user_p_R.message(F.text)  # Декоратор для обработки текстовых сообщений
# async def start_command(message: types.Message):
#     await message.answer(f"Эхо: {message.text}")
#         # users_database.register(message)

# @user_p_R.message(Command("menu"))
# async def menu_command(message: types.Message):
