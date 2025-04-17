from aiogram import Router, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

router = Router()

@router.message(commands=["start"])
async def start_handler(message: types.Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Старт 🚀")]],
        resize_keyboard=True,
        one_time_keyboard=True
    )

    await message.answer(
        "Привіт! 👋\n"
        "Я – бот Інженерного Ярмарку Кар’єри й допоможу тобі дізнатися про всі наші активності, спікерів та оновлення.\n"
        "Щоб розпочати наше знайомство натисни «Старт 🚀»!",
        reply_markup=keyboard
    )
