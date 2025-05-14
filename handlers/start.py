from aiogram import Router, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from keyboards.main_menu_kb import main_menu_kb
from utils.database import get_user
# from aiogram.types.input_file import FSInputFile


router = Router()

@router.message(Command("start"))
async def start_handler(message: types.Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Старт 🚀")]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    user_data = await get_user(message.from_user.id)
    is_registered = user_data is not None

    if is_registered:
        first_name = user_data.get("name", "").split()[0] if user_data.get("name") else ""
        text = (
            f"Радий знову тебе бачити, <b>{first_name}!</b> 👋\n\n"
            "Зараз на панелі ти бачиш <b>розділи</b> – тисни на них, щоб дізнатись більше деталей про кожен блок 🔎."
        )
        await message.answer(
            text=text,
            reply_markup=main_menu_kb(),
            parse_mode="HTML"
        )
    else:
        await message.answer(
            text=(
                "Привіт!👋\n\n"
                "Я – бот <b>Інженерного Ярмарку Кар’єри</b> й допоможу тобі дізнатися про всі наші активності, спікерів, оновлення та навіть створити СV.\n\n"
                "Щоб розпочати наше знайомство натисни <b>«Старт 🚀»</b>!"
            ),
            reply_markup=keyboard,
            parse_mode="HTML"
        )