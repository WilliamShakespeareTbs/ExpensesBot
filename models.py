import config

from datetime import datetime
from sqlalchemy import BigInteger, ForeignKey, Table, Column, MetaData, String, func
from sqlalchemy.orm import relationship, Mapped, mapped_column, DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

engine = create_async_engine(config.SQLALCHEMY_URL, echo=False)
async_session = async_sessionmaker(engine)
metadata_obj = MetaData()

class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger)


class Category(Base):
    __tablename__ = 'categories'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(20))
    sum: Mapped[float] = mapped_column()
    user_id: Mapped[BigInteger] = mapped_column(ForeignKey('users.id'))


class Expense(Base):
    __tablename__ = 'expenses'

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[datetime] = mapped_column(server_default=func.now())
    sum: Mapped[float] = mapped_column()
    comment: Mapped[str | None] = mapped_column(String(100))
    category: Mapped[str] = mapped_column(ForeignKey('categories.id'))


async def async_main():
    async with engine.connect() as conn:
    #    await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        pass