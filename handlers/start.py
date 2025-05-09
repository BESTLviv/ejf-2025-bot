from aiogram import Router, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from keyboards.main_menu_kb import main_menu_kb
from utils.database import get_user


router = Router()

@router.message(Command("start"))
async def start_handler(message: types.Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Старт 🚀")]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    user_data = await get_user(message.from_user.id)
    is_registered = user_data is not None and user_data.get("registered", False)

    if is_registered:
        first_name = user_data.get("first_name", "").split()[0] if user_data.get("first_name") else ""
        await message.answer(
            f"Радий знову тебе бачити, {first_name}! 👋\n"
            "Зараз на панелі ти бачиш розділи – тисни на них, щоб дізнатись більше деталей про кожен блок 🔎.",
            reply_markup=main_menu_kb(),
            parse_mode="HTML"
        )
    else:
        await message.answer(
            "Привіт! 👋\n"
            "Я – бот <b>Інженерного Ярмарку Кар'єри</b> й допоможу тобі дізнатися про всі наші активності, спікерів та оновлення.\n"
            "Щоб розпочати наше знайомство натисни «Старт 🚀»!",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
