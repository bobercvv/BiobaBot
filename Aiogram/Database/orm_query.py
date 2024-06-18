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
        user_item_num=len(list(user_item_num))+1,
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

# Получение товаров из корзины конкретного пользователя по id
async def orm_user_get_cart(session: AsyncSession, user_id: int):
    query = select(Product).where(Product.user_id == user_id)
    result = await session.execute(query)
    return result.scalars().all()

# Получение товара с переданным номером из корзины пользователя
async def orm_user_get_item(session: AsyncSession, user_id: int, num_of_item: int):
    query = select(Product).where(Product.user_id == user_id and num_of_item == Product.user_item_num)
    result = await session.execute(query)
    return result.scalars().all()

# Изменение товара в корзине
async def orm_update_item(session: AsyncSession, product_number: int, data: dict, message: types.Message):
    query = select(Product).where(message.from_user.id == Product.user_id)
    user_item_num = await session.execute(query)
    query = update(Product).where(Product.id == product_number).values(
        user_id=message.from_user.id,
        username=message.from_user.first_name,
        user_item_num=len(list(user_item_num)) + 1,
        name_product=data['name_product'],
        type_product=data['type_product'],
        cost_product=float(data['cost_product']),)
    await session.execute(query)
    await session.commit()

# Удаление записи из БД
async def orm_delete_item(session: AsyncSession, user_id: int, num_of_item: int):
    query = delete(Product).where(Product.user_id == user_id and num_of_item == Product.user_item_num)
    await session.execute(query)
    await session.commit()

# Получение числа - количество товаров из корзины пользователя
async def orm_user_count_items(session: AsyncSession, message: types.Message):
    query = select(Product).where(message.from_user.id == Product.user_id)
    user_item_num = await session.execute(query)
    return len(list(user_item_num))