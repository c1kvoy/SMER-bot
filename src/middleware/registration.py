from aiogram import BaseMiddleware
from aiogram.types import Message, Update
from sqlalchemy.future import select
from src.database import session, Users

class RegistrationMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Update, data: dict):
        if isinstance(event, Message) and event.from_user:
            user_id = event.from_user.id
            if event.text == "/register" or event.text == "/start":
                return await handler(event, data)
            async with session() as db:
                query = select(Users).where(Users.user_id == user_id)
                result = await db.execute(query)
                user = result.scalars().first()

            if not user:
                await event.answer("Вы не зарегистрированы. Пожалуйста, используйте /register для регистрации.")
                return
        return await handler(event, data)