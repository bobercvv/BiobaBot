from aiogram import types, Router, F, Bot  # Библиотека aiogram

from aiogram.enums import ParseMode # Указывание Parse Mode для сообщений (Markdown/HTML)
from aiogram.filters import Command, or_f, Filter, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from sqlalchemy.ext.asyncio import AsyncSession

from ..Common.filters import ChatFilter, IsAdmin, IsNum
from ..Common.reply_keyboards import admin_kbd, del_kbd

# ROUTER
admin_R = Router() #admin_router - роутер для работы с админами
admin_R.message.filter(ChatFilter(['private']), IsAdmin())

ADMINS_LIST = [994559549]


@admin_R.message(Command('admin'))
async def chatInfo_command(message: types.Message):
    await message.answer("Вы перенаправлены в меню администратора", reply_markup=admin_kbd)


# ОТМЕНА И СБРОС ВВОДА
# Сброс ввода
@admin_R.message(StateFilter('*'), or_f(Command('cancel'), F.text.casefold() == 'отмена',F.text.casefold() == 'cancel'))
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
@admin_R.message(SetCurrency.currency, IsNum())
async def changeCurrency(message: types.Message, state: FSMContext):
    await state.update_data(currency=float(message.text))
    await message.answer("Курс CNY был обновлён")
    data = await state.get_data()
    await message.answer(f"Актуальный курс равен: {data['currency']}", reply_markup=admin_kbd)
    await state.clear()
@admin_R.message(SetCurrency.currency)
async def changeCurrencyI(message: types.Message):
    await message.answer("Введены некорректные данные. Повторите ввод")


# ПОЛУЧЕНИЕ СПИСКА ТОВАРОВ
@admin_R.message(or_f(Command('get_products_database'), F.text.lower() == 'получить список товаров'))
async def setCurrency(message: types.Message, session: AsyncSession):
    await message.answer("СПИСОК ТОВАРОВ", reply_markup=admin_kbd)



# ПОЛУЧЕНИЕ ИНФОРМАЦИИ О ЧАТЕ
@admin_R.message(or_f(F.text.lower() == 'информация о чате', Command('chat_info')))
async def chatInfo_command(message: types.Message):
    await message.answer(str(message), reply_markup=admin_kbd)