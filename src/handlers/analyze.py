from aiogram import Router
from aiogram.types import Message, ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from datetime import datetime, timedelta

from sqlalchemy.orm import join
from src.database import session, Diary, Users
from sqlalchemy import select, and_

router = Router()


@router.message(Command("average"))
async def summary(message: Message):
    now = datetime.now()
    periods = {
        "сутки": now - timedelta(days=1),
        "неделю": now - timedelta(weeks=1),
        "месяц": now - timedelta(days=30)
    }

    results = []

    async with session() as db:
        for period_name, start_date in periods.items():
            query = select(Diary.reaction).select_from(
                join(Diary, Users, Diary.login == Users.login)
            ).where(
                and_(
                    Users.user_id == message.from_user.id,
                    Users.is_logged_in == True,
                    Diary.timestamp >= start_date,
                    Diary.timestamp <= now
                )
            )
            grades = await db.execute(query)
            rows = grades.scalars().all()
            grades = [row for row in rows]

            if grades:
                average = sum(grades) / len(grades)
                results.append(f"Средняя за {period_name}: {average:.2f}")
            else:
                results.append(f"Нет данных за {period_name}")
    response = "\n".join(results)
    await message.answer(response)
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="/add")],
            [KeyboardButton(text="/average")],
            [KeyboardButton(text="/export")]
        ],
        resize_keyboard=True
    )
    await message.answer(
        "Что вы хотите сделать дальше?",
        reply_markup=keyboard
    )