from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

def get_cv_type_kb():
    buttons = [
        [KeyboardButton(text="⚡️ Створити резюме разом")],
        [KeyboardButton(text="⚡️ Завантажити своє резюме")],
        [KeyboardButton(text="⚡️ Повернутись до блоків")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def has_cv_kb():
    buttons = [
        [KeyboardButton(text="✏️ Повернутись до блоків")],
        [KeyboardButton(text="✏️ Редагувати попередній варіант")],
        [KeyboardButton(text="✏️ Так, хочу додати ще одне CV")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)                  

def change_cv_type_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Бажана посада", callback_data="edit_position"),
             InlineKeyboardButton(text="Володіння мовами", callback_data="edit_languages")],
            [InlineKeyboardButton(text="Освіта", callback_data="edit_education"),
             InlineKeyboardButton(text="Досвід", callback_data="edit_experience")],
            [InlineKeyboardButton(text="Навички", callback_data="edit_skills"),
             InlineKeyboardButton(text="Про кандидата", callback_data="edit_about")],
            [InlineKeyboardButton(text="Контакти", callback_data="edit_contacts")],
            [InlineKeyboardButton(text="Підтвердити зміни", callback_data="confirm_editing")]
        ]
    )