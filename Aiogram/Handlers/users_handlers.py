# Библиотека aiogram
from aiogram import types, Router, F

# FSM machine
from aiogram.fsm import state
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

# DATABASE
from sqlalchemy.ext.asyncio import AsyncSession

# AIOGRAM MODULES
# filters
from aiogram.filters import Command, or_f, StateFilter
# text formatting
from aiogram.utils.formatting import Bold, as_list, as_marked_list, as_marked_section  # Функции для форматирования текста
# Указывание Parse Mode для сообщений (Markdown/HTML)
from aiogram.enums import ParseMode

# MODULES
# database
from Aiogram.Database.orm_query import orm_add_product
# reply keyboards
from Aiogram.Common.reply_keyboards import start_kbd, del_kbd, menu_kbd, type_product_kbd, make_kbd
# filters
from Aiogram.Common.filters import IsNum, InCategories
# currency
from Aiogram.Modules import currencies
# browser - Работа с браузером для перенаправления на сайт
import webbrowser


# ROUTER
user_p_R = Router() # user_private_router - роутер для работы с обработчиками комманд для обычных пользователей



# HANDLER'ы ОТМЕНЫ И СБРОСА ВВОДА
# Переход в меню
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
    if str(current_state) == "Cart:action":
        await message.answer("<b>Предыдущего шага нет.</b>\n"
                             "<i>для отмены изменения корзины и перехода в меню нажмите /cancel</i>", parse_mode=ParseMode.HTML, reply_markup=make_kbd("Добавить товар", "Удалить товар", sizes=(2,)))
        await message.answer("Выберите действие, которое хотите совершить")
        return

    previous_step = None
    for step in GetCurrency.__all_states__:
        if step.state == current_state:
            await state.set_state(previous_step)
            await message.answer(f"<i>Вы вернулись в прошлому шагу</i>: \n\n{GetCurrency.texts[previous_step.state]}", parse_mode=ParseMode.HTML)
            return
        previous_step = step
    for step in Cart.__all_states__:
        if step.state == current_state:
            await state.set_state(previous_step)
            await message.answer(f"<i>Вы вернулись в прошлому шагу</i>:\n{Cart.texts[previous_step.state][0]}", reply_markup=Cart.texts[previous_step.state][1], parse_mode=ParseMode.HTML)
            return
        if str(step.state) != 'Cart:name_product': previous_step = step






# Расчёт стоимости товара & /currency
class GetCurrency(StatesGroup):
    value = State()
    texts = {
        "SetCurrency:value": "Введите стоимость товара в CNY\n\n"
                             "<i>для выхода в меню нажмите /cancel</i>"
    }

@user_p_R.message(StateFilter(None), or_f(Command("currency"), F.text.casefold() == 'расчёт стоимости товара'))
async def currency_command(message: types.Message, state: FSMContext):
    await message.answer("Введите стоимость товара в CNY\n<i>для перехода в меню нажмите /cancel</i>", parse_mode=ParseMode.HTML, reply_markup=del_kbd)
    await state.set_state(GetCurrency.value)

@user_p_R.message(GetCurrency.value, IsNum())
async def currency_command(message: types.Message, state: FSMContext):
    await state.update_data(value=float(message.text))
    data = await state.get_data()
    await message.answer(f"Расчётная стоимость товара составляет: {round(float(currencies.TO_RUB('CNY')) * data['value'], 2)} RUB")
    await message.answer(f"Для повторного расчёта стоимости нажмите /currency\n"
                         f"Для перехода в меню нажмите /menu")
    await state.clear()

@user_p_R.message(GetCurrency.value)
async def currency_command(message: types.Message):
    await message.answer("Введены некорректные данные. Повторите ввод")






# КОРЗИНА
# Содержимое корзины
@user_p_R.message(or_f(Command("cart"), F.text.casefold() == 'моя корзина'))
async def cart_content(message: types.Message):
    await message.answer("Вот что находится в вашей корзине сейчас:\n\n"
                         "Для изменения корзины нажмите /edit_cart", reply_markup=del_kbd)

class Cart(StatesGroup):
    action = State() # выбор действия: удаление или добавление товара в корзине
    type_product = State() # ввод категории товара
    action_name = State() # выбор ввода наименования товара
    name_product = State() # ввод наименования товара
    cost_product = State() # ввод стоимости товара в CNY

    texts = {
        'Cart:action': ["Выберите действие, которое хотите совершить", make_kbd("Добавить товар", "Удалить товар", sizes=(2,))],
        'Cart:type_product': ["Выберите категорию товара", type_product_kbd],
        'Cart:action_name': ["Желаете добавить наименованеи товара?", make_kbd("Да", "Нет", sizes=(2,))],
        'Cart:name_product': ["Введите наименование товара", del_kbd],
    }

# Редактирование корзины
@user_p_R.message(StateFilter(None), or_f(Command("edit_cart"), F.text.casefold() == 'изменить корзину'))
async def cart_edit(message: types.Message, state: FSMContext):
    await message.answer(f"<b>Вот что находится в вашей корзине:</b>\n\n"
                         f"СОДЕРЖИМОЕ КОРЗИНЫ\n\n"
                         f"<i>для перехода в меню нажмите /cancel</i>", parse_mode=ParseMode.HTML)
    await message.answer(f"Выберите действие, которое хотите совершить\n", reply_markup=make_kbd("Добавить товар", "Удалить товар", sizes=(2,)))
    await state.set_state(Cart.action)


# ДОБАВЛЕНИЕ товара в корзину
@user_p_R.message(Cart.action, F.text.lower() == "добавить товар")
async def cart_edit_add(message: types.Message, state: FSMContext):
    await state.update_data(action='add')
    await message.answer("<b>Вы перешли к добавлению товара</b>\n"
                         f"<i>для отмены добавления товара нажмите /cancel\n"
                         f"для перехода к предыдущему действию нажмите /back</i>", parse_mode=ParseMode.HTML)
    await message.answer("Выберите категорию товара", reply_markup=type_product_kbd)
    await state.set_state(Cart.type_product)

# категория товара
@user_p_R.message(Cart.type_product, InCategories())
async def cart_add_type(message: types.Message, state: FSMContext):
    await state.update_data(type_product=message.text)
    await message.answer("Желаете добавить наименование товара?\n",
                         parse_mode=ParseMode.HTML, reply_markup=make_kbd("Да", "Нет", sizes=(2,)))
    await state.set_state(Cart.action_name)
@user_p_R.message(Cart.type_product)
async def cart_add_typeI(message: types.Message):
    await message.answer(f"<b>Такой категории нет, повторите ввод.</b>\n"
                         f"<i>для отмены добавления товара нажмите /cancel\n"
                         f"для изменения выбора действия в корзине нажмите /back</i>", parse_mode=ParseMode.HTML, reply_markup=type_product_kbd)
    await message.answer(f"Выберите категорию товара")

# выбор добавления наименования
@user_p_R.message(Cart.action_name, or_f(F.text.casefold() == "да", F.text.casefold() == "yes"))
async def cart_add_action_nameY(message: types.Message, state: FSMContext):
    await state.update_data(action_name='yes')
    await message.answer("Введите наименование товара", reply_markup=del_kbd)
    await state.set_state(Cart.name_product)
@user_p_R.message(Cart.action_name, or_f(F.text.casefold() == "нет", F.text.casefold() == "no"))
async def cart_add_action_nameN(message: types.Message, state: FSMContext):
    await state.update_data(action_name='no')
    await state.update_data(name_product='')
    await message.answer("Введите стоимость товара в CNY", reply_markup=del_kbd)
    await state.set_state(Cart.cost_product)
@user_p_R.message(Cart.action_name)
async def cart_add_action_nameI(message: types.Message):
    await message.answer(f"<b>Некорректый ввод. Повторите попытку.</b>\n"
                         f"<i>для отмены добавления товара нажмите /cancel\n"
                         f"для возврата к выбору категории товара нажмите /back</i>", parse_mode=ParseMode.HTML, reply_markup=make_kbd("Да", "Нет", sizes=(2,)))
    await message.answer(f"Желаете добавить наименование товара?")

# добавление наименования товара
@user_p_R.message(Cart.name_product, F.text)
async def cart_add_name(message: types.Message, state: FSMContext):
    await state.update_data(name_product=message.text)
    await message.answer("Введите стоимость товара в CNY", reply_markup=del_kbd)
    await state.set_state(Cart.cost_product)
@user_p_R.message(Cart.name_product)
async def cart_add_nameI(message: types.Message):
    await message.answer("<b>Неверное наименование. Повторите ввод.</b>\n"
                         "<i>для отмены добавления товара нажмите /cancel\n"
                         "для возврата к выбору добавления наименования товара нажмите /back</i>", parse_mode=ParseMode.HTML)

# стоимость товара и запись данных в БД
@user_p_R.message(Cart.cost_product, F.text, IsNum())
async def cart_add_cost(message: types.Message, state: FSMContext, session: AsyncSession):
    await state.update_data(cost_product=float(message.text))
    data = await state.get_data()
    if data['action_name'] == 'no':  data['name_product'] = data['type_product']

    # try:
    # Добавление записи о товаре в БД
    await orm_add_product(message, session, data)
    # Сообщение об успешном занесении данных и очищение состояния
    await message.answer(f"<b>Данный товар был успешно добавлен в корзину:</b>\n\n"
                         f"<b>{data['name_product']}</b>\n"
                         f"Категория товара: {data['type_product']}\n"
                         f"Стоимость товара в CNY: {data['cost_product']}\n", parse_mode=ParseMode.HTML)
    await state.clear()
    await cart_edit(message, state)
    # except Exception:
    #     await message.answer("<b>Ошибка добавления товара в корзину.</b>\nОбратитесь в поддержку:\n@bobercvv", parse_mode=ParseMode.HTML)
    #     await state.clear()
@user_p_R.message(Cart.cost_product)
async def cart_add_costI(message: types.Message):
     await message.answer("<b>Некорректный ввод.</b>\n"
                          "<i>для отмены добавления товара нажмите /cancel\n"
                          "для возврата к выбору наименования товара нажмите /back</i>", parse_mode=ParseMode.HTML)
     await message.answer("Введите стоимость товара в CNY")

@user_p_R.message(Cart.action)
async def cart_editI(message: types.Message):
    await message.answer(f"<b>Такой комманды нет.</b>\n"
                         f"<i>для отмены изменения корзины и перехода в меню нажмите /cancel</i>", parse_mode=ParseMode.HTML, reply_markup=make_kbd("Добавить товар", "Удалить товар", sizes=(2,)))
    await message.answer(f"Выберите действие, которое хотите совершить")





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
    await message.answer_photo(photo='AgACAgIAAxkBAAIDjmZmJuMvfJkQN-JiPQ_sNWMml_5BAAIo2jEbxbYxSzyH8_tpxSHfAQADAgADeAADNQQ')
    await message.answer("Вы перенаправлены в меню BiobaBot 😤.\n"
                         "Здесь Вы можете рассчитать примерную стоимость товара с учетом доставки.\n"
                         "Для оформеления заказа напишите нам в личные сообщения: /contacts",
                         reply_markup=menu_kbd)



# SITE
@user_p_R.message(or_f(Command("site"), F.text.lower() == "сайт", F.text.lower() == "перейти на сайт", F.text.lower() == "сайт"))
async def site_command(message): # Перенаправление на сайт Bioba
    await message.answer('Открывается сайт Bioba', reply_markup=del_kbd)
    webbrowser.open('http://bioba.ru/')



# CONTACTS
@user_p_R.message(or_f(Command("contacts"), F.text.lower() == "контакты"))
async def contacts_command(message):
    await message.answer("Для оформления заказа обращайтесь сюда: \n@biobadelivery", reply_markup=del_kbd)



# DELIVERY
@user_p_R.message(or_f(Command("delivery"), F.text.lower() == 'с каких площадок доставляете?'))
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
async def photo_handler(message: types.Message):
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
