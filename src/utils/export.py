import pandas as pd
from sqlalchemy.future import select
from datetime import datetime
from src.database import session, Diary

async def export_to_excel(user_id: int) -> str:
    async with session() as db:
        query = select(Diary.time_period, Diary.situation, Diary.reaction, Diary.thoughts, Diary.emotions, Diary.timestamp).where(
            Diary.user_id == user_id
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