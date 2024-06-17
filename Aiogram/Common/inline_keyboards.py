from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_callback_btns(
        *,
        btns: dict[str, str],
        sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()

    for text, data in btns.items():
        keyboard.add(InlineKeyboardButton(text=text, callback_data=data))

    return keyboard.adjust(*sizes).as_markup()


def get_url_btns(
        *,
        btns: dict[str, str],
        sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()

    for text, url in btns.items():
        keyboard.add(InlineKeyboardButton(text=text, url=url))

    return keyboard.adjust(*sizes).as_markup()


# Создать микс из CallBack и URL кнопок
def get_inlineMix_btns(
        *,
        btns: dict[str, str],
        sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()

    for text, value in btns.items():
        if '://' in value:
            keyboard.add(InlineKeyboardButton(text=text, url=value))
        else:
            keyboard.add(InlineKeyboardButton(text=text, callback_data=value))

    return keyboard.adjust(*sizes).as_markup()

cart_kbd_inl = get_callback_btns(btns={"Изменить корзину": "to_edit_cart",
                                       "Рассчитать стоимость корзины": "get_cost_cart"},sizes=(1,1))

cart_actions_inl = get_callback_btns(btns={"Добавить товар": "add_item",
                                           "Изменить товар": "update_item",
                                           "Удалить товар": "delete_item",
                                           "Отменить редактирование": "cancel"}, sizes=(1,1,1,1))

kategories_inl = get_callback_btns(btns={"Обувь": "Обувь",
                                   "Футболка": "Футболка",
                                   "Штаны": "Штаны",
                                   "Нижнее бельё": "Нижнее бельё",
                                   "Верхняя одежда": "Верхняя одежда",
                                   "Аксессуар": "Аксессуар",
                                   "Отменить редактирование": "cancel",
                                   "Назад": "back"}, sizes=(2,2,2,1,1))

w_or_not_name_inl = get_callback_btns(btns={"Да": "with_name",
                                        "Нет":"without_name",
                                        "Назад":"back",
                                        "Отменить редактирование":"cancel"}, sizes=(2,1,1))

back_n_cancel_inl = get_callback_btns(btns={"Назад":"back", "Отменить редактирование":"cancel"}, sizes=(2,))