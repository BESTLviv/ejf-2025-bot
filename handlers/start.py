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
    # and user_data.get("registered", False)
    if is_registered:
        first_name = user_data.get("name", "").split()[0] if user_data.get("name") else ""
       
        caption = (f"Радий знову тебе бачити, {first_name}! 👋\n","Зараз на панелі ти бачиш розділи – тисни на них, щоб дізнатись більше деталей про кожен блок 🔎.")
        await message.answer(
        caption=caption,
        reply_markup=main_menu_kb(),
        parse_mode="HTML")

    else:
        await message.answer(
            "Привіт!\n"
            "Я – бот Інженерного Ярмарку Кар’єри й допоможу тобі дізнатися про всі наші активності, спікерів, оновлення та навіть створити СV.\n"
            "Щоб розпочати наше знайомство натисни «Старт 🚀»!",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    # photo_path = "media/ejf.jpg" 
    # caption = ("📢 <b>Інженерний Ярмарок Кар’єри</b> — це місце, де ти зможеш познайомитися з топовими компаніями, дізнатись про вакансії, а також взяти участь у цікавих активностях.\n"
    # "Тепер, познайомимося ближче!")
    # await message.answer_photo(
    #     photo=FSInputFile(photo_path),
    #     caption=caption,
    #     reply_markup=keyboard,
    #     parse_mode="HTML")
