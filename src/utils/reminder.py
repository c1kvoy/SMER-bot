from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot
from sqlalchemy.future import select
from src.database import session, Users, Diary
from datetime import date

async def send_reminder(bot: Bot, time_period: str):
    async with session() as db:
        query_users = select(Users.user_id)
        result_users = await db.execute(query_users)
        all_users = result_users.scalars().all()

        today = date.today()
        query_latest = select(Diary.user_id).where(
            (Diary.timestamp >= today) & (Diary.time_period == time_period)
        )
        result_latest = await db.execute(query_latest)
        users_with_diary = result_latest.scalars().all()

    users_to_remind = set(all_users) - set(users_with_diary)

    if time_period == "утро":
        reminder_message = "Доброе утро! Как вы себя чувствуете? Пора заполнить дневник."
    elif time_period == "день":
        reminder_message = "Как проходит ваш день? Не забудьте оценить свое состояние в дневнике."
    elif time_period == "вечер":
        reminder_message = "Как прошел ваш день? Заполните дневник перед сном."
    else:
        reminder_message = "Не забудьте заполнить дневник!"

    for user_id in users_to_remind:
        await bot.send_message(
            user_id,
            reminder_message
        )

def setup_reminders(bot: Bot):
    scheduler = AsyncIOScheduler()

    scheduler.add_job(
        send_reminder,
        "cron",
        hour=8,
        args=[bot, "утро"]
    )

    scheduler.add_job(
        send_reminder,
        "cron",
        hour=13,
        args=[bot, "день"]
    )


    scheduler.add_job(
        send_reminder,
        "cron",
        hour=21,
        args=[bot, "вечер"]
    )

    scheduler.start()