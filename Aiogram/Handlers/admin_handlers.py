from aiogram import types, Router, F, Bot  # Библиотека aiogram

from aiogram.enums import ParseMode # Указывание Parse Mode для сообщений (Markdown/HTML)
from aiogram.filters import Command, or_f, Filter, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from ..Common.filters import ChatFilter, IsAdmin, IsNum
from ..Common.reply_keyboards import admin_kbd, del_kbd

# ROUTER
admin_R = Router() #admin_router - роутер для работы с админами
admin_R.message.filter(ChatFilter(['private']), IsAdmin())

ADMINS_LIST = [994559549]


@admin_R.message(Command('admin'))
async def chatInfo_command(message: types.Message):
    await message.answer("Вы перенаправлены в меню администратора", reply_markup=admin_kbd)

@admin_R.message(Command('chat_info'))
async def chatInfo_command(message: types.Message):
    await message.answer(str(message))




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

# Установка курса CNY
class SetCurrency(StatesGroup):
    currency = State()
    val = State()

    texts = {
        "SetCurrency:currency": "Введите курс заново",
        "SetCurrency:val": "Введите валюту заново"
    }
# Ввод курса
@admin_R.message(StateFilter(None), or_f(Command('setcurrency'), F.text.lower() == 'изменить курс cny'))
async def setCurrency(message: types.Message, state: FSMContext):
    await message.answer("Введите курс, который вы хотите установить:", reply_markup=del_kbd)
    await state.set_state(SetCurrency.currency)

# Обработка сообщения и переход к вводу валюты
@admin_R.message(SetCurrency.currency, IsNum())
async def changeCurrency(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Курс CNY был обновлён")
    await message.answer("Введите валюту")
    await state.set_state(SetCurrency.val)

@admin_R.message(SetCurrency.currency)
async def changeCurrency(message: types.Message):
    await message.answer("Введены некорректные данные. Повторите ввод")

# Обработка ввода валюты
@admin_R.message(SetCurrency.val, F.text)
async def changeCurrency(message: types.Message, state: FSMContext):
    await state.update_data(val=message.text)
    await message.answer("Валюта изменена")
    data = await state.get_data()
    await message.answer(str(data))
    await state.clear()

@admin_R.message(SetCurrency.val)
async def changeCurrency(message: types.Message):
    await message.answer("Введены некорректные данные. Повторите ввод")