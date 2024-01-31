import asyncio
import os
import sys

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    NullPool, Text, Boolean,
)
from sqlalchemy.ext.asyncio import AsyncAttrs, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from config import DB_link

# Настройка базы данных

engine = create_async_engine(DB_link, poolclass=NullPool)
async_session = async_sessionmaker(engine, expire_on_commit=False)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id = Column(String(255), primary_key=True)

    username = Column(String(255))
    lang = Column(String(255))
    create_time = Column(DateTime)
    last_start_time = Column(DateTime)

    status = Column(String(255))
    car_id = Column(String(255))

class Bid(Base):
    __tablename__ = "bids"
    id = Column(String(255), primary_key=True)

    user_id = Column(String(255))
    post_id = Column(String(255))

    create_time = Column(DateTime)


class Post(Base):
    __tablename__ = "posts"
    id = Column(String(255), primary_key=True)

    car_name = Column(String(255))

    images = Column(Text)
    not_ready_images = Column(Text)
    text = Column(Text)

    information = Column(Text)
    information_files = Column(Text, default="")
    information_files_upload_status = Column(Boolean, default=False)

    post_date = Column(DateTime)
    posted_status = Column(Boolean, default=False)

    upload_status = Column(Boolean, default=False)

    create_time = Column(DateTime)


async def async_create_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def async_drop_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


if __name__ == "__main__":
    asyncio.run(async_drop_db())
    asyncio.run(async_create_db())
