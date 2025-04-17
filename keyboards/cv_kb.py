from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_cv_type_kb():
    buttons = [
        [KeyboardButton(text="📝 Створити CV")],
        [KeyboardButton(text="⬅️ Назад")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
