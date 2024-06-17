from aiogram import types, Router, F, Bot  # Библиотека aiogram

from aiogram.enums import ParseMode # Указание Parse Mode для сообщений (Markdown/HTML)
from aiogram.filters import Command, or_f, Filter, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from sqlalchemy.ext.asyncio import AsyncSession

from ..Common.filters import ChatFilter, IsAdmin, IsNumMsg
from ..Common.reply_keyboards import admin_kbd, del_kbd

# ROUTER
from ..Database.orm_query import orm_admin_get_all_products

admin_R = Router() #admin_router - роутер для работы с админами
admin_R.message.filter(ChatFilter(['private']), IsAdmin())

ADMINS_LIST = [994559549, 1033874041] # @bobercvv, @belsky


@admin_R.message(Command('admin'))
async def admin_menu(message: types.Message):
    await message.answer("Вы перенаправлены в меню администратора.", reply_markup=admin_kbd)
    await message.answer("Доступные комманды:\n"
                         "/setcurrency - установить курс CNY\n"
                         "/get_products_database - получить список корзин всех пользователей\n"
                         "/chat_info - информация о чате", reply_markup=admin_kbd)


# ОТМЕНА И СБРОС ВВОДА
# Сброс ввода
@admin_R.message(StateFilter('*'), or_f(Command('cancel'), F.text.casefold() == 'отмена', F.text.casefold() == 'cancel'))
async def cancel(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.clear()

    await message.answer("Вы перенаправлены в меню администратора", reply_markup=admin_kbd)

# Комманда назад
@admin_R.message(StateFilter('*'), or_f(Command('back'), F.text.casefold() == 'назад', F.text.casefold() == 'back'))
async def back(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()

    if str(current_state) == "SetCurrency:currency":
        await message.answer("Предыдущего шага нет, для отмены ввода нажмите /cancel")
        return

    previous_step = None
    for step in SetCurrency.__all_states__:
        if step.state == current_state:
            await state.set_state(previous_step)
            await message.answer(f"<i>Вы вернулись в прошлому шагу</i>: \n\n{SetCurrency.texts[previous_step.state]}", parse_mode=ParseMode.HTML)
            return
        previous_step = step


# УСТАНОВКА КУРСА
class SetCurrency(StatesGroup):
    currency = State()

    texts = {
        "SetCurrency:currency": "Введите курс заново"
    }
# Ввод курса
@admin_R.message(StateFilter(None), or_f(Command('setcurrency'), F.text.lower() == 'изменить курс cny'))
async def setCurrency(message: types.Message, state: FSMContext):
    await message.answer("Введите курс, который вы хотите установить:", reply_markup=del_kbd)
    await state.set_state(SetCurrency.currency)
# Изменение и сохранение курса валюты
@admin_R.message(SetCurrency.currency, IsNumMsg())
async def changeCurrency(message: types.Message, state: FSMContext):
    await state.update_data(currency=float(message.text))
    await message.answer("Курс CNY был обновлён")
    data = await state.get_data()
    await message.answer(f"Актуальный курс равен: {data['currency']}", reply_markup=del_kbd)
    await state.clear()
    await admin_menu(message)
@admin_R.message(SetCurrency.currency)
async def changeCurrencyI(message: types.Message):
    await message.answer("Введены некорректные данные. Повторите ввод")


# ПОЛУЧЕНИЕ СПИСКА ТОВАРОВ
@admin_R.message(or_f(Command('get_products_database'), F.text.lower() == 'получить список товаров'))
async def get_products_database(message: types.Message, session: AsyncSession):
    prod_data = dict()
    for product in await orm_admin_get_all_products(session):
        if product.username not in prod_data.keys(): prod_data[product.username] = []
        prod_data[str(product.username)] += [f'<b><i>Товар №{product.user_item_num}</i></b>\n'
                                        f'Название: {product.name_product}\n'
                                        f'Категория: {product.type_product}\n'
                                        f'Стоимость в CNY: {round(product.cost_product, 2)}']

    str_data = str()
    for i in prod_data.keys():
        str_data += f"<b>Корзина пользователя {i}:</b>\n\n"
        for j in prod_data[i]:
            str_data += j + "\n"
    str_data += '\n'
    await message.answer(str_data, parse_mode=ParseMode.HTML, reply_markup=del_kbd)
    await admin_menu(message)


# ПОЛУЧЕНИЕ ИНФОРМАЦИИ О ЧАТЕ
@admin_R.message(or_f(F.text.lower() == 'информация о чате', Command('chat_info'), F.text.lower() == 'инфа'))
async def chatInfo_command(message: types.Message):
    await message.answer(f"Айдишник: {message.from_user.id}")
    await message.answer(str(message), reply_markup=del_kbd)
    await admin_menu(message)