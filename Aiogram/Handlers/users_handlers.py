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
from Aiogram.Common.inline_keyboards import cart_kbd_inl, get_callback_btns, cart_actions_inl, kategories_inl, \
    w_or_not_name_inl, back_n_cancel_inl, go_to_cart
from Aiogram.Database.orm_query import orm_add_product, orm_user_count_items, orm_user_get_cart, orm_delete_item, \
    orm_user_get_item, orm_clean_cart
# reply keyboards
from Aiogram.Common.reply_keyboards import start_kbd, del_kbd, menu_kbd, type_product_kbd, make_kbd, cart_actions, \
    cart_kbd
# filters
from Aiogram.Common.filters import IsNumMsg, InCategories, IsNumCall, IsIntMsg
# currency
from Aiogram.Modules import currencies
# browser - Работа с браузером для перенаправления на сайт
import webbrowser

from Aiogram.Modules.currencies import TO_RUB

# ROUTER
user_p_R = Router() # user_private_router - роутер для работы с обработчиками комманд для обычных пользователей


# HANDLER'ы ОТМЕНЫ И СБРОСА ВВОДА
# Переход в меню
@user_p_R.callback_query(StateFilter('*'), F.data == 'cancel')
async def cancel(callback: types.CallbackQuery, state: FSMContext) -> None:
    # Удаление сообщений "Вы перешли к..." при выборе действия в корзине
    global data_msg_for_back_del
    if data_msg_for_back_del:
        await data_msg_for_back_del.delete()
        data_msg_for_back_del = 0
    # Получение текущего состояния
    current_state = await state.get_state()
    # Если текущее состояние не определено
    if current_state is None:
        return
    # Очищение состояния, вывод сообщения и перенаправление в меню бота
    await state.clear()
    await callback.message.edit_text("Действие было отменено.", reply_markup=None)
    await menu_command(callback.message)

# Комманда назад
@user_p_R.callback_query(StateFilter('*'), F.data == 'back')
async def back(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    # Удаление сообщений "Вы перешли к..." при выборе действия в корзине
    global data_msg_for_back_del
    if data_msg_for_back_del:
        await data_msg_for_back_del.delete()
        data_msg_for_back_del = 0
    # Получение текущего состояния
    current_state = await state.get_state()
    # Если нажимается кнопка "назад" при вводе номера товара для удаления
    if str(current_state) == "Cart:num_of_item": current_state = Cart.type_product

    if str(current_state) == "Cart:action":
        await callback.message.edit_text("Выберите действие, которое хотите совершить", reply_markup=cart_actions_inl)
        return

    previous_step = None
    for step in Cart.__all_states__:
        if step.state == current_state:
            await state.set_state(previous_step)
            if not (await orm_user_get_cart(session, callback.message.from_user.id)) and current_state == 'Cart:type_product':
                await callback.message.edit_text(f"Выберите действие, которое хотите совершить",
                                                 reply_markup=get_callback_btns(btns={"Добавить товар": "add_item",
                                                                                      "Отменить редактирование": "cancel"},
                                                                                      sizes=(1,1)),
                                                 parse_mode=ParseMode.HTML)
            else:
                await callback.message.edit_text(f"{Cart.texts[previous_step.state][0]}",
                                          reply_markup=Cart.texts[previous_step.state][1], parse_mode=ParseMode.HTML)
            return
        # Условие для сохранения перехода в позапредыдущему шагу
        if str(step.state) != 'Cart:name_product': previous_step = step






# Расчёт стоимости товара & /currency
class GetCurrency(StatesGroup):
    value = State()


@user_p_R.message(StateFilter(None), or_f(Command("currency"),
                  F.text.casefold() == 'раcсчёт стоимости товара', F.text.casefold() == "рассчитать стоимость снова"))
async def currency_command(message: types.Message, state: FSMContext):
    await message.answer("Введите стоимость товара в CNY",
                         parse_mode=ParseMode.HTML, reply_markup=get_callback_btns(btns={"Отменить действие":"cancel"}))
    await state.set_state(GetCurrency.value)

@user_p_R.message(GetCurrency.value, IsNumMsg())
async def currency_command(message: types.Message, state: FSMContext):
    await state.update_data(value=float(message.text))
    data = await state.get_data()
    await message.answer(f"Расчётная стоимость товара составляет: "
                         f"{round(float(currencies.TO_RUB('CNY')) * data['value'], 2)} RUB",
                         reply_markup=get_callback_btns(btns={"Перейти в меню": "go_to_menu", "Рассчитать стоимость снова": "currency_again"}, sizes=(1,)))
    await state.clear()

@user_p_R.callback_query(StateFilter(None), F.data == "currency_again")
async def currency_command(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Введите стоимость товара в CNY",
                         parse_mode=ParseMode.HTML, reply_markup=get_callback_btns(btns={"Отменить действие":"cancel"}))
    await state.set_state(GetCurrency.value)

@user_p_R.message(GetCurrency.value)
async def currency_command(message: types.Message):
    await message.answer("Введены некорректные данные. Повторите ввод")





# КОРЗИНА
@user_p_R.callback_query(F.data == "to_cart")
async def cart_content_call(callback: types.CallbackQuery, session: AsyncSession):
    await cart_content(callback.message, session)

# Содержимое корзины
@user_p_R.message(StateFilter(None), or_f(Command("cart"), F.text.casefold() == 'моя корзина', F.text.casefold() == 'посмотреть корзину'))
async def cart_content(message: types.Message, session: AsyncSession):
    have_items = False # Флаг, что в корзине есть товары
    cart_dict = dict() # Словарь, куда записываются данные из корзины пользователя
    for product in await orm_user_get_cart(session, message.from_user.id):
        have_items = True # Флаг, что в корзине есть товары
        cart_dict[product.user_item_num] = {'name': product.name_product,
                                            'type': product.type_product,
                                            'cost': product.cost_product}
    cart_s_l = [f'<b><i>Товар №{i}</i></b>\n'
                f'Название: {cart_dict[i]["name"]}\n'
                f'Категория: {cart_dict[i]["type"]}\n'
                f'Стоимость в CNY: {round(cart_dict[i]["cost"], 2)}\n'
                f'Стоимость в рублях: {round(cart_dict[i]["cost"] * TO_RUB("CNY"), 2)}\n' for i in cart_dict.keys()]
    cart_str = str()
    for i in cart_s_l:
        cart_str += i + "\n"
    if have_items:
        await message.answer(f"Вот что находится в вашей корзине сейчас:\n\n"
                             f"{cart_str}", parse_mode=ParseMode.HTML, reply_markup=cart_kbd_inl)
    else:
        await message.answer("Ваша корзина пуста.",
                             parse_mode=ParseMode.HTML,
                             reply_markup=get_callback_btns(btns={"Изменить корзину": "to_edit_cart"}))


# ПОЛУЧЕНИЕ СТОИМОСТИ КОРЗИНЫ
@user_p_R.callback_query(F.data == "get_cost_cart")
async def get_cart_currency(callback: types.CallbackQuery, session: AsyncSession):
    cart_currency = float()
    for product in await orm_user_get_cart(session, callback.from_user.id):
        cart_currency += round(float(currencies.TO_RUB('CNY')) * float(product.cost_product), 2)
    await callback.message.answer(f"Рассчётная стоимость вашей корзины составляет: {round(cart_currency,2)} RUB",
                                  parse_mode=ParseMode.HTML)


# ОЧИЩЕНИЕ КОРЗИНЫ
@user_p_R.callback_query(F.data == "to_clean_cart")
async def clean_cart(callback: types.CallbackQuery, session: AsyncSession):
    print(int(callback.message.from_user.id))
    await orm_clean_cart(session, int(callback.message.from_user.id))
    await callback.message.delete_reply_markup()
    await callback.message.answer(f"Ваша корзина была очищена.", parse_mode=ParseMode.HTML)

class Cart(StatesGroup):
    action = State() # выбор действия в корзине
    type_product = State() # ввод категории товара
    action_name = State() # выбор ввода наименования товара
    name_product = State() # ввод наименования товара
    cost_product = State() # ввод стоимости товара в CNY

    num_of_item = State() # Номер товара (для удаления)

    texts = {
        'Cart:action': ["Выберите действие, которое хотите совершить", cart_actions_inl],
        'Cart:type_product': ["Выберите категорию товара", kategories_inl],
        'Cart:action_name': ["Желаете добавить наименование товара?", w_or_not_name_inl],
        'Cart:name_product': ["Введите наименование товара", back_n_cancel_inl]

    }

# Редактирование корзины
# @user_p_R.message(StateFilter(None), or_f(Command("edit_cart"), F.text.casefold() == 'изменить корзину'))
@user_p_R.callback_query(F.data == "to_edit_cart")
async def cart_edit(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    cart_dict = dict()
    have_items = False
    for product in await orm_user_get_cart(session, callback.from_user.id):
        have_items = True # Флаг непустой корзины
        cart_dict[product.user_item_num] = {'name': product.name_product,
                                            'type': product.type_product,
                                            'cost': product.cost_product}
    cart_s_l = [f'<b><i>Товар №{i}</i></b>\n'
                f'Название: {cart_dict[i]["name"]}\n'
                f'Категория: {cart_dict[i]["type"]}\n'
                f'Стоимость в CNY: {round(cart_dict[i]["cost"], 2)}\n'
                f'Стоимость в рублях: {round(cart_dict[i]["cost"] * TO_RUB("CNY"),2)}\n' for i in cart_dict.keys()]
    cart_str = str()
    for i in cart_s_l:
        cart_str += i + "\n"


    if have_items:
        await callback.message.edit_text(f"<b>Вот что находится в вашей корзине сейчас:</b>\n\n"
                                         f"{cart_str}", parse_mode=ParseMode.HTML)
        await callback.message.answer(f"Выберите действие, которое хотите совершить\n",
                                      reply_markup=cart_actions_inl)
    else:
        await callback.message.edit_text(f"Ваша корзина пуста.", parse_mode=ParseMode.HTML)
        await callback.message.answer(f"Выберите действие, которое хотите совершить\n",
                                      reply_markup=get_callback_btns(btns={"Добавить товар": "add_item",
                                                                           "Отменить редактирование": "cancel"},
                                                                     sizes=(1,1)))
    await state.set_state(Cart.action)


# ДОБАВЛЕНИЕ товара в корзину
@user_p_R.callback_query(Cart.action, F.data == "add_item")
async def cart_edit_add(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(action='add')
    await callback.message.delete()
    global data_msg_for_back_del
    data_msg_for_back_del = await callback.message.answer("<b>Вы перешли к добавлению товара</b>\n", parse_mode=ParseMode.HTML)
    await callback.message.answer("Выберите категорию товара", reply_markup=kategories_inl)
    await state.set_state(Cart.type_product)

# категория товара
@user_p_R.callback_query(Cart.type_product, InCategories())
async def cart_add_type(callback: types.CallbackQuery, state: FSMContext):
    global data_msg_for_back_del
    data_msg_for_back_del = 0
    await state.update_data(type_product=callback.data)
    await callback.message.delete()
    await callback.message.answer("Желаете добавить наименование товара?\n", parse_mode=ParseMode.HTML,
                                  reply_markup=w_or_not_name_inl)
    await state.set_state(Cart.action_name)
@user_p_R.message(Cart.type_product)
async def cart_add_typeI(message: types.Message):
    await message.delete()
    await message.answer(f"<b>Такой категории нет. Выберите категорию еще раз.</b>\n", parse_mode=ParseMode.HTML)

# добавление наименования
@user_p_R.callback_query(Cart.action_name, F.data == "with_name")
async def cart_add_action_nameY(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await state.update_data(action_name='with_name')
    global msg
    msg = await callback.message.answer("Введите наименование товара",
                                  reply_markup=back_n_cancel_inl)
    await state.set_state(Cart.name_product)
# без наименования
@user_p_R.callback_query(Cart.action_name, F.data == "without_name")
async def cart_add_action_nameN(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await state.update_data(action_name='without_name')
    await state.update_data(name_product='')
    global msg
    msg = await callback.message.answer("Введите стоимость товара в CNY",
                                  reply_markup=back_n_cancel_inl)

    await state.set_state(Cart.cost_product)
@user_p_R.message(Cart.action_name)
async def cart_add_action_nameI(message: types.Message):
    await message.delete()
    await message.answer(f"<b>Некорректый ввод. Повторите попытку.</b>\n", parse_mode=ParseMode.HTML)

# добавление наименования товара
@user_p_R.message(Cart.name_product, F.text)
async def cart_add_name(message: types.Message, state: FSMContext):
    global msg
    await msg.delete_reply_markup()
    await state.update_data(name_product=message.text)
    msg = await message.answer("Введите стоимость товара в CNY",
                         reply_markup=back_n_cancel_inl)
    await state.set_state(Cart.cost_product)
@user_p_R.message(Cart.name_product)
async def cart_add_nameI(message: types.Message):
    await message.answer("<b>Недопустимое наименование. Повторите ввод.</b>\n",
                         parse_mode=ParseMode.HTML)

# стоимость товара и запись данных в БД
@user_p_R.message(Cart.cost_product, F.text, IsNumMsg())
async def cart_add_cost(message: types.Message, state: FSMContext, session: AsyncSession):
    global msg
    await msg.delete_reply_markup()
    await state.update_data(cost_product=float(message.text))
    data = await state.get_data()
    if data['action_name'] == 'without_name':  data['name_product'] = data['type_product']

    # try:
    # Добавление записи о товаре в БД
    await orm_add_product(message, session, data)
    # Сообщение об успешном занесении данных и очищении состояния
    await message.answer(f"<b>Данный товар был успешно добавлен в корзину:</b>\n\n"
                         f"<b>{data['name_product']}</b>\n"
                         f"Категория товара: {data['type_product']}\n"
                         f"Стоимость в CNY: {data['cost_product']}\n"
                         f"Стоимость в рублях: {round(data['cost_product'] * float(TO_RUB('CNY')),2)}\n", parse_mode=ParseMode.HTML,
                         reply_markup=go_to_cart)
    await state.clear()
    # except Exception:
    #     await message.answer("<b>Ошибка добавления товара в корзину.</b>\nОбратитесь в поддержку:\n@bobercvv", parse_mode=ParseMode.HTML)
    #     await state.clear()
    #     await menu_command(message)
@user_p_R.message(Cart.cost_product)
async def cart_add_costI(message: types.Message):
     await message.delete()
     await message.answer("<b>Некорректный ввод. Повторите попытку</b>\n", parse_mode=ParseMode.HTML)






# УДАЛЕНИЕ товара из корзины
@user_p_R.callback_query(Cart.action, F.data == "delete_item")
async def cart_edit_del(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("<b>Введите номер товара в корзине, который хотите удалить</b>\n",
                                  parse_mode=ParseMode.HTML, reply_markup=back_n_cancel_inl)
    await state.set_state(Cart.num_of_item)

@user_p_R.message(Cart.num_of_item, IsIntMsg())
async def cart_edit_del_num_item(message: types.Message, state: FSMContext, session: AsyncSession):
    s = await orm_user_count_items(session, message)
    if s >= int(message.text) >= 1:
        del_item_data = {}
        for product in await orm_user_get_item(session, message.from_user.id, int(message.text)):
            del_item_data["name"] = product.name_product
            del_item_data["type"] = product.type_product
            del_item_data["cost"] = product.cost_product
        await orm_delete_item(session, message.from_user.id, int(message.text))
        await message.answer(f"<b>Данный товар был успешно удалён из вашей корзины:</b>\n\n"
                             f"<b>Товар №{message.text}</b>\n"
                             f"С наименованием: {del_item_data['name']}\n"
                             f"Стоимостью {round(del_item_data['cost'],2)} CNY\n\n", reply_markup=go_to_cart, parse_mode=ParseMode.HTML)
        await state.clear()
    else:
        await cart_edit_del_num_itemI(message)
@user_p_R.message(Cart.num_of_item)
async def cart_edit_del_num_itemI(message: types.Message):
    await message.delete()
    await message.answer("<b>Товара с таким номером нет. Повторите ввод.</b>\n", parse_mode=ParseMode.HTML)

# РЕДАКТИРОВАНИЕ ПРЕДМЕТА В КОРЗИНЕ
class EditItemInCart(StatesGroup):
    num_of_item = State()  # Номер товара
    edit_type = State() # ввод категории товара
    edit_name = State() # выбор ввода наименования товара
    edit_cost = State() # ввод стоимости товара в CNY

    texts = {
        'Cart:action': ["Выберите действие, которое хотите совершить", cart_actions_inl],
        'Cart:type_product': ["Выберите категорию товара", kategories_inl],
        'Cart:action_name': ["Желаете добавить наименование товара?", w_or_not_name_inl],
        'Cart:name_product': ["Введите наименование товара", back_n_cancel_inl]

    }

@user_p_R.callback_query(Cart.action, F.data == "update_item")
async def cart_edit_update(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    await callback.message.answer("<b>Введите номер товара в корзине, который хотите отредактировать</b>\n",
                                  parse_mode=ParseMode.HTML, reply_markup=back_n_cancel_inl)
    await state.set_state(EditItemInCart.num_of_item)

@user_p_R.callback_query(EditItemInCart.num_of_item, IsNumMsg())
async def cart_edit_update(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    await callback.message.answer("<b>Введите номер товара в корзине, который хотите отредактировать</b>\n",
                                  parse_mode=ParseMode.HTML, reply_markup=back_n_cancel_inl)
    await state.set_state(EditItemInCart.num_of_item)
@user_p_R.callback_query(EditItemInCart.num_of_item, IsNumMsg())
async def cart_edit_update(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    await callback.message.answer("<b>Введите номер товара в корзине, который хотите отредактировать</b>\n",
                                  parse_mode=ParseMode.HTML, reply_markup=back_n_cancel_inl)
    await state.set_state(EditItemInCart.num_of_item)






@user_p_R.message(Cart.action)
async def cart_editI(message: types.Message):
    await message.delete()
    await message.answer(f"<b>Такой комманды нет.</b>\n",
                         parse_mode=ParseMode.HTML)





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
@user_p_R.callback_query(StateFilter(None), F.data == 'go_to_menu')
async def menu_command_call(callback: types.CallbackQuery):
    await callback.message.edit_reply_markup(reply_markup=del_kbd)
    await callback.message.answer_photo(photo='AgACAgIAAxkBAAIDjmZmJuMvfJkQN-JiPQ_sNWMml_5BAAIo2jEbxbYxSzyH8_tpxSHfAQADAgADeAADNQQ',
                               caption="Вы перенаправлены в меню BiobaBot 😤.\n"
                               "Здесь Вы можете рассчитать примерную стоимость товара с учетом доставки.",
                               reply_markup=menu_kbd)

@user_p_R.message(StateFilter(None), or_f(Command("menu"), F.text.casefold() == "меню", F.text.casefold() == "перейти в меню", F.text.casefold() == "вернуться в меню"))
async def menu_command(message: types.Message):
    await message.answer_photo(photo='AgACAgIAAxkBAAIDjmZmJuMvfJkQN-JiPQ_sNWMml_5BAAIo2jEbxbYxSzyH8_tpxSHfAQADAgADeAADNQQ',
                               caption="Вы перенаправлены в меню BiobaBot 😤.\n"
                               "Здесь Вы можете рассчитать примерную стоимость товара с учетом доставки.",
                               reply_markup=menu_kbd)


# SITE
@user_p_R.message(or_f(Command("site"), F.text.lower() == "сайт", F.text.lower() == "перейти на сайт", F.text.lower() == "сайт"))
async def site_command(message): # Перенаправление на сайт Bioba
    await message.answer('Открывается сайт Bioba', reply_markup=del_kbd)
    webbrowser.open('http://bioba.ru/')



# CONTACTS
@user_p_R.message(or_f(Command("contacts"), F.text.lower() == "наши контакты"))
async def contacts_command(message):
    await message.answer("Для оформления заказа обращайтесь сюда: \n@biobadelivery", reply_markup=del_kbd)



# DELIVERY
@user_p_R.message(or_f(Command("delivery"), F.text.lower() == 'с каких площадок доставляете?'))
async def delivery_command(message: types.Message):
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



msg: types.Message = False # Удаление клавиатур для сообщений с ответами message
data_msg_for_back_del: types.Message = 0 # Удаление сообщений "Вы перешли к..." при переходе к предыдшему шагу
