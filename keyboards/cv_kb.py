from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_cv_type_kb():
    buttons = [
        [KeyboardButton(text="Створити резюме разом")],
        [KeyboardButton(text="Завантажити своє резюме")],
        [KeyboardButton(text="Повернутись до блоків")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
