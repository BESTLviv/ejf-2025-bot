import asyncio
from aiogram import Bot, Dispatcher
from config import load_config
from handlers import registration, menu, admin, broadcast
from middlewares.auth import AuthMiddleware
from utils.database import get_database

config = load_config()

bot = Bot(token=config.bot_token, parse_mode="HTML")
dp = Dispatcher()

async def main():
    db = await get_database()
    
    dp.message.middleware(AuthMiddleware(db))
    
    dp.include_routers(
        registration.router,
        menu.router,
        admin.router,
        broadcast.router,
    )
    
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
