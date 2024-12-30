from sqlalchemy import DateTime
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped
from sqlalchemy import Integer, String, Text, DateTime
from config import DATABASE_URL

class Base(DeclarativeBase):
    pass


engine = create_async_engine(DATABASE_URL)
session = async_sessionmaker(bind=engine, expire_on_commit=False, autoflush=False, autocommit=False)

class Diary(Base):
    __tablename__ = 'diary'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)  # ID пользователя Telegram
    time_period: Mapped[str] = mapped_column(String, nullable=False)  # Утро, День, Вечер
    situation: Mapped[str] = mapped_column(Text, nullable=True)  # Описание ситуации
    reaction: Mapped[str] = mapped_column(Text, nullable=True)  # Реакция
    thoughts: Mapped[str] = mapped_column(Text, nullable=True)  # Мысли
    emotions: Mapped[str] = mapped_column(Text, nullable=True)  # Эмоции
    timestamp: Mapped[DateTime] = mapped_column(DateTime, nullable=False)



async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
