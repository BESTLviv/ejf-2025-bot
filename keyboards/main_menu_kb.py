from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_menu_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📅  Розклад"), KeyboardButton(text="📂 CV")],
            [KeyboardButton(text="🎯 Гра Share and Win"), KeyboardButton(text="👥 Чат з учасниками")],
            [KeyboardButton(text="🗣️ Спікери"), KeyboardButton(text="🩵💛 Підтримка ЗСУ")]
        ],
        resize_keyboard=True
    )
