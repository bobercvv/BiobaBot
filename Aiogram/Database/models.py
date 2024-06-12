from sqlalchemy import String, Float, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    created: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

class Product(Base):
    __tablename__ = 'cart_items'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(nullable=False)
    username: Mapped[str] = mapped_column(String(50), nullable=False)
    user_item_num: Mapped[int] = mapped_column(nullable=False)
    name_product: Mapped[str] = mapped_column(String(150), nullable=False)
    type_product: Mapped[str] = mapped_column(String(50), nullable=False)
    cost_product: Mapped[float] = mapped_column(Float(asdecimal=True), nullable=False)