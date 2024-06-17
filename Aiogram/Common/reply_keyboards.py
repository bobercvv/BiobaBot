from aiogram import types
from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton, KeyboardButtonPollType
from aiogram.utils.keyboard import ReplyKeyboardBuilder


async def del_reply_kbd(message: types.Message):
    await bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=message.message_id - 1)


def make_kbd(
        *btns: str,
        placeholder: str = None,
        request_contact: int = None,
        request_location: int = None,
        sizes: tuple[int]
):
    '''
    Parameters request_contact and request_location must be as indexes of btns args for buttons you need.
    Example:
    get_keyboard(
            "Меню",
            "О магазине",
            "Варианты оплаты",
            "Варианты доставки",
            "Отправить номер телефона",
            placeholder="Что вас интересует?",
            request_contact=4,
            sizes=(2, 2, 1)
        )
    '''
    keyboard = ReplyKeyboardBuilder()

    for index, text in enumerate(btns, start=0):

        if request_contact and request_contact == index:
            keyboard.add(KeyboardButton(text=text, request_contact=True))

        elif request_location and request_location == index:
            keyboard.add(KeyboardButton(text=text, request_location=True))
        else:
            keyboard.add(KeyboardButton(text=text))

    return keyboard.adjust(*sizes).as_markup(
        resize_keyboard=True, input_field_placeholder=placeholder)




# КЛАВИТУРЫ

# УДАЛЕНИЕ КЛАВИАТУРЫ
del_kbd = ReplyKeyboardRemove()



# СТАРТОВАЯ КЛАВИАТУРА
start_kbd = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Меню"),
        ],
        [
            KeyboardButton(text="Расчёт стоимости товара"),
            KeyboardButton(text="С каких площадок доставляете?"),
        ],
        [
            KeyboardButton(text="Сайт"),
            KeyboardButton(text="Контакты"),
        ]
    ],
    resize_keyboard=True, input_field_placeholder="Нажмите на одну из кнопок ниже"
)



# МЕНЮ КЛАВИАТУРА
menu_kbd = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Раcсчёт стоимости товара"),
            KeyboardButton(text="Моя корзина"),
        ],
        [
            KeyboardButton(text="Наши контакты"),
        ],
        [
            KeyboardButton(text="FAQ"),
        ]
    ],
    resize_keyboard=True, input_field_placeholder="Нажмите на одну из кнопок ниже", one_time_keyboard=True
)

# КЛАВИАТУРА ТИПОВ ТОВАРОВ
categories = ["обувь", "футболка", "штаны", "нижнее бельё", "верхняя одежда", "аксессуар"]
type_product_kbd = ReplyKeyboardMarkup(keyboard=[
        [
            KeyboardButton(text="Обувь"),
            KeyboardButton(text="Футболка"),
            KeyboardButton(text="Штаны"),
        ],
        [
            KeyboardButton(text="Нижнее бельё"),
            KeyboardButton(text="Верхняя одежда"),
            KeyboardButton(text="Аксессуар")
        ],
        [
            KeyboardButton(text="Отменить редактирование"),
            KeyboardButton(text="Назад")
        ]
    ],
    resize_keyboard=True, input_field_placeholder="Нажмите на одну из кнопок ниже"
)

# Клавиатура на странице корзины
cart_kbd = make_kbd("Рассчитать стоимость корзины",
                    "Изменить корзину",
                    "Перейти в меню",
                    sizes=(2,1))

# Клавиатура редактирования корзины
cart_actions = make_kbd("Добавить товар",
                        "Изменить товар",
                        "Удалить товар",
                        "Отменить редактирование",
                        sizes=(3,1,))


# ТЕСТОВАЯ КЛАВИАТУРА
test_kbd = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Получение контактов", request_contact=True),
            KeyboardButton(text="Получение геопозиции", request_location=True),
            KeyboardButton(text="Создать опрос", request_poll=KeyboardButtonPollType())
        ]
    ],
    resize_keyboard=True, input_field_placeholder="Нажмите на одну из кнопок ниже"
)



# АДМИНСКАЯ КЛАВИАТУРА
admin_kbd = make_kbd(
    "Изменить курс CNY",
    "Получить список товаров",
    "Информация о чате",
    sizes=(1,1,1)
)



