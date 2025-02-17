from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand, BotCommandScopeDefault

# from src.middleware.gigachat import get_gigachat_token
from src.utils.reminder import setup_reminders
from src.config import BOT_TOKEN
from src.handlers.handlers import router
from src.database import init_db
from aiogram.fsm.storage.memory import MemoryStorage
from src.middleware.registration import RegistrationMiddleware
from src.handlers.registration import router as registration_router
from src.handlers.export import router as export_router
from src.handlers.analyze import router as analyze_router

storage = MemoryStorage()
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=storage)


async def main():
    commands = [
                BotCommand(command='add', description='Добавление записи'),
                BotCommand(command='average', description='Средняя оценка за период'),
                BotCommand(command='export', description='Экспорт дневника в Excel'),
                BotCommand(command='register', description='Регистрация'),
                BotCommand(command='login', description='Вход в аккаунт'),
                BotCommand(command='logout', description='Выход из аккаунта'),
                ]
    await bot.set_my_commands(commands, BotCommandScopeDefault())
    await init_db()
    setup_reminders(bot)
    dp.include_router(registration_router)
    router.message.outer_middleware(RegistrationMiddleware())
    export_router.message.outer_middleware(RegistrationMiddleware())
    analyze_router.message.outer_middleware(RegistrationMiddleware())
    dp.include_router(router)
    dp.include_router(export_router)
    dp.include_router(analyze_router)
    await dp.start_polling(bot)



if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
