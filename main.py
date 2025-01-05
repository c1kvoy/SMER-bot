from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand, BotCommandScopeDefault
from src.utils.reminder import setup_reminders
from src.config import BOT_TOKEN
from src.handlers.handlers import router
from src.database import init_db
from aiogram.fsm.storage.memory import MemoryStorage
from src.middleware.registration import RegistrationMiddleware
from src.handlers.registration import router as registration_router
from src.handlers.export import router as export_router

storage = MemoryStorage()
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=storage)


async def main():
    commands = [BotCommand(command='register', description='Регистрация'),
                BotCommand(command='start', description='Начало диалога'),
                BotCommand(command='add', description='Добавление записи'),
                BotCommand(command='export', description='Экспорт дневника в Excel')]
    await bot.set_my_commands(commands, BotCommandScopeDefault())
    await init_db()
    setup_reminders(bot)
    dp.include_router(registration_router)
    router.message.outer_middleware(RegistrationMiddleware())
    export_router.message.outer_middleware(RegistrationMiddleware())
    dp.include_router(router)
    dp.include_router(export_router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
