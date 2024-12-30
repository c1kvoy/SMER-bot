from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from database import init_db
bot = Bot(token=BOT_TOKEN)

async def main():
    await init_db()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())