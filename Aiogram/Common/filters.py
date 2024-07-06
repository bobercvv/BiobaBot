import os

from aiogram import Bot, types
from aiogram.filters import Filter
from aiogram.types import Message
from sqlalchemy import select, text, create_engine
from sqlalchemy.ext.asyncio import AsyncSession

from Aiogram.Common.reply_keyboards import categories
from Aiogram.Database.engine import engine, session_maker
from Aiogram.Database.models import Product
from Aiogram.Database.orm_query import orm_user_count_items


class ChatFilter(Filter):
    def __init__(self, chat_types: list[str]) -> None:
        self.chat_types = chat_types

    async def __call__(self, message: Message) -> bool:
        return message.chat.type in self.chat_types

class IsAdmin(Filter):
    def __init__(self) -> None:
        pass
    async def __call__(self, message: Message, bot: Bot) -> bool:
        from ..Handlers.admin_handlers import ADMINS_LIST
        return message.chat.id in ADMINS_LIST

class IsNumMsg(Filter):
    async def __call__(self, message: Message, bot: Bot) -> bool:
        try:
            text = message.text
            text = text.replace(',', '.')
            if (str(float(text)) == text) or (str(int(text)) == text):
                return True
            else:
                return False
        except Exception:
            return False

class IsIntMsg(Filter):
    async def __call__(self, message: Message, bot: Bot) -> bool:
        try:
            text = message.text
            if (str(int(text)) == text):
                return True
            else:
                return False
        except Exception:
            return False

class IsNumCall(Filter):
    async def __call__(self, callback: types.CallbackQuery, bot: Bot) -> bool:
        # try:
        text = callback.data
        print("FEFE")
        text = text.replace(',', '.')
        if (str(float(text)) == text) or (str(int(text)) == text):
            return True
        else:
            return False
        # except Exception:
        #     return False

class InCategories(Filter):
    async def __call__(self, callback: types.CallbackQuery, bot: Bot) -> bool:
        if (callback.data.lower() in categories):
            return True
        else:
            return False

# class ItemInCart(Filter):
#     async def __call__(self, message: Message, bot: Bot):
#         # try:
#         # text = message.text
#         from ..Handlers.users_handlers import s
#         query = select(Product).where(message.from_user.id == Product.user_id)
#         print("________________________",s)
#         z = await s.execute(query)



        # except Exception:
        #     return False