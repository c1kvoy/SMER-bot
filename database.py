from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, relationship
from sqlalchemy import Integer, String, Text, DateTime, ForeignKey
from config import DATABASE_URL

class Base(DeclarativeBase):
    pass


engine = create_async_engine(DATABASE_URL)
session = async_sessionmaker(bind=engine, expire_on_commit=False, autoflush=False, autocommit=False)

class Diary(Base):
    __tablename__ = 'diary'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.user_id"), nullable=False)
    time_period: Mapped[str] = mapped_column(String, nullable=False)
    situation: Mapped[str] = mapped_column(Text, nullable=True)
    reaction: Mapped[str] = mapped_column(Text, nullable=True)
    thoughts: Mapped[str] = mapped_column(Text, nullable=True)
    emotions: Mapped[str] = mapped_column(Text, nullable=True)
    timestamp: Mapped[DateTime] = mapped_column(DateTime, nullable=False)

    user: Mapped["Users"] = relationship(back_populates="diaries")

class Users(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)

    diaries: Mapped[list[Diary]] = relationship("Diary", back_populates="user")


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
