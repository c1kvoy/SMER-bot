from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand, BotCommandScopeDefault

from config import BOT_TOKEN
from handlers import router
from database import init_db
from aiogram.fsm.storage.memory import MemoryStorage

storage = MemoryStorage()
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=storage)


async def main():
    commands = [BotCommand(command='start', description='Начало диалога'),
                BotCommand(command='add', description='Добавление записи')]
    await bot.set_my_commands(commands, BotCommandScopeDefault())
    await init_db()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
