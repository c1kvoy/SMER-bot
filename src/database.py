from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, relationship
from sqlalchemy import Integer, String, Text, DateTime, ForeignKey, Boolean
from src.config import DATABASE_URL

class Base(DeclarativeBase):
    pass


engine = create_async_engine(DATABASE_URL)
session = async_sessionmaker(bind=engine, expire_on_commit=False, autoflush=False, autocommit=False)

class Diary(Base):
    __tablename__ = 'diary'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer)
    login: Mapped[int] = mapped_column(String, ForeignKey("users.login"), nullable=False)
    time_period: Mapped[str] = mapped_column(String, nullable=False)
    situation: Mapped[str] = mapped_column(Text, nullable=True)
    reaction: Mapped[int] = mapped_column(Integer, nullable=True)
    thoughts: Mapped[str] = mapped_column(Text, nullable=True)
    emotions: Mapped[str] = mapped_column(Text, nullable=True)
    timestamp: Mapped[DateTime] = mapped_column(DateTime, nullable=False)

    user: Mapped["Users"] = relationship(back_populates="diaries")

class Users(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    login: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String, nullable=False)
    is_logged_in: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    diaries: Mapped[list["Diary"]] = relationship("Diary", back_populates="user")

class Messages(Base):
    __tablename__ = 'messages'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=True)
    target: Mapped[str] = mapped_column(Text, nullable=True)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
