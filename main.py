import asyncio
from aiogram import Bot, Dispatcher
from config import load_config
from handlers import registration, menu, admin, broadcast, cv, start 
from middlewares.auth import AuthMiddleware
from utils.database import get_database
from handlers import cv

config = load_config()

bot = Bot(token=config.bot_token)
dp = Dispatcher()


async def main():
    bot.session.default_parse_mode = "HTML"
    db = await get_database()
    
    dp.message.middleware(AuthMiddleware(db))
    
    dp.include_routers(
        start.router,
        registration.router,
        menu.router, 
        admin.router,
        cv.router 
    )
    
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())