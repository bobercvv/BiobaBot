from aiogram import types
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from Aiogram.Database.models import Product

# Добавление товара в БД
async def orm_add_product(message: types.Message, session: AsyncSession, data: dict):
    query = select(Product).where(message.from_user.id == Product.user_id)
    user_item_num = await session.execute(query)
    item = Product(
        user_id=message.from_user.id,
        username=message.from_user.first_name,
        user_item_num=0,
        name_product=data['name_product'],
        type_product=data['type_product'],
        cost_product=float(data['cost_product']),
    )
    # Запись данных в БД
    session.add(item)
    # Закрепление изменений в БД
    await session.commit()

# Получение всех записей товаров из БД
async def orm_admin_get_all_products(session: AsyncSession):
    query = select(Product)
    result = await session.execute(query)
    return result.scalars().all()

# Получение товаров из корзины пользователя
async def orm_get_user_cart(session: AsyncSession, user_id: int):
    query = select(Product).where(Product.user_id == user_id)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_update_item(session: AsyncSession, product_number: int, data):
    query = update(Product).where(Product.id == product_number).values(
        name=data["name"],
        description=data["description"],
        price=float(data["price"]),
        image=data["image"],)
    await session.execute(query)
    await session.commit()


async def orm_delete_product(session: AsyncSession, product_id: int):
    query = delete(Product).where(Product.id == product_id)
    await session.execute(query)
    await session.commit()