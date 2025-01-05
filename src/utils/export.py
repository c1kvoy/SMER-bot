import pandas as pd
from sqlalchemy.future import select
from sqlalchemy.orm import join
from sqlalchemy import and_
from datetime import datetime
from src.database import session, Diary, Users


async def export_to_excel(user_id: int) -> str:
    async with session() as db:
        query = select(
            Diary.time_period,
            Diary.situation,
            Diary.reaction,
            Diary.thoughts,
            Diary.emotions,
            Diary.timestamp
        ).select_from(
            join(Diary, Users, Diary.login == Users.login)
        ).where(
            and_(
                Users.user_id == user_id,
                Users.is_logged_in == True
            )
        )
        result = await db.execute(query)
        rows = result.fetchall()

    data = [
        {
            "Время дня": row.time_period,
            "Ситуация": row.situation,
            "Реакция": row.reaction,
            "Мысли": row.thoughts,
            "Эмоции": row.emotions,
            "Время записи": row.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        }
        for row in rows
    ]
    df = pd.DataFrame(data)
    filename = f"diary_export_{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
    filepath = f"./{filename}"
    df.to_excel(filepath, index=False, engine="openpyxl")

    return filepath
