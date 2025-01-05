from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand, BotCommandScopeDefault
from src.reminder import setup_reminders
from src.config import BOT_TOKEN
from src.handlers import router
from src.database import init_db
from aiogram.fsm.storage.memory import MemoryStorage
from src.registration_middleware import RegistrationMiddleware
from src.registration import router as registration_router
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent / 'src'))


storage = MemoryStorage()
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=storage)


async def main():
    commands = [BotCommand(command='register', description='Регистрация'),
                BotCommand(command='start', description='Начало диалога'),
                BotCommand(command='add', description='Добавление записи')]
    await bot.set_my_commands(commands, BotCommandScopeDefault())
    await init_db()
    setup_reminders(bot)
    dp.include_router(registration_router)
    router.message.outer_middleware(RegistrationMiddleware())
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
