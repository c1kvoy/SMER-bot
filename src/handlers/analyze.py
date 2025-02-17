from aiogram import Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from datetime import datetime, timedelta

from requests.packages import target
from sqlalchemy import and_
from src.database import session, Diary, Messages
from src.middleware.gigachat import LangChainService
from sqlalchemy import insert, select

router = Router()

langchain_service = LangChainService()

@router.message(Command("average"))
async def summary(message: Message):
    now = datetime.now()
    periods = {
        "сутки": now - timedelta(days=1),
        "неделю": now - timedelta(weeks=1),
        "месяц": now - timedelta(days=30),
    }

    results = []
    analysis_data = []

    async with session() as db:
        for period_name, start_date in periods.items():
            query = select(Diary.reaction, Diary.situation, Diary.thoughts, Diary.emotions).where(
                and_(
                    Diary.user_id == message.from_user.id,
                    Diary.timestamp >= start_date,
                    Diary.timestamp <= now
                )
            )
            result = await db.execute(query)
            rows = result.all()

            if rows:
                reactions = [row.reaction for row in rows if row.reaction]
                situations = [row.situation for row in rows if row.situation]
                thoughts = [row.thoughts for row in rows if row.thoughts]
                emotions = [row.emotions for row in rows if row.emotions]

                if reactions:
                    average = sum(reactions) / len(reactions)
                    results.append(f"Средняя за {period_name}: {average:.2f}")
                else:
                    results.append(f"Средняя за {period_name}: Нет данных")

                analysis_data.append(
                    f"Период: {period_name}\n"
                    f"Ситуации: {'; '.join(situations) if situations else 'Нет данных'}\n"
                    f"Мысли: {'; '.join(thoughts) if thoughts else 'Нет данных'}\n"
                    f"Эмоции: {'; '.join(emotions) if emotions else 'Нет данных'}\n"
                )
            else:
                results.append(f"Нет данных за {period_name}")

    if analysis_data:
        analysis_text = "\n\n".join(analysis_data)
        gigachat_response = await langchain_service.analyze_user_data(analysis_text)
    else:
        gigachat_response = "Недостаточно данных для анализа."

    response = "\n".join(results)
    final_response = f"{response}\n\nРекомендации:\n{gigachat_response}"

    await message.answer(final_response)

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


@router.message()
async def default_message_handler(message: Message):

    user_id = message.from_user.id
    user_input = message.text

    async with session() as db:
        save_user_stmt = insert(Messages).values(
            user_id=user_id,
            text=user_input,
            target="from"
        )
        await db.execute(save_user_stmt)
        await db.commit()

        history_stmt = (
            select(Messages.text, Messages.target)
            .where(Messages.user_id == user_id)
            .order_by(Messages.id.desc())
            .limit(10)
        )
        result = await db.execute(history_stmt)
        history = []
        for row in result:
            history.append([row.text, row.target])

    response = await langchain_service.process_user_message(
        user_history=history,
        user_input=user_input
    )

    async with session() as db:
        save_bot_stmt = insert(Messages).values(
            user_id=user_id,
            text=response,
            target="to"
        )
        await db.execute(save_bot_stmt)
        await db.commit()

    await message.answer(response)
