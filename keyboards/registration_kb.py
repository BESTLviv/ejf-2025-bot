from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_course_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="1 курс"), KeyboardButton(text="2 курс")],
            [KeyboardButton(text="3 курс"), KeyboardButton(text="4 курс")],
            [KeyboardButton(text="Магістратура")],
            [KeyboardButton(text="Не навчаюсь"), KeyboardButton(text="Ще у школі/коледжі")]
        ],
        resize_keyboard=True
    )

def get_university_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="НУ “ЛП”"), KeyboardButton(text="ЛНУ ім. І. Франка")],
            [KeyboardButton(text="УКУ"), KeyboardButton(text="ЛНАМ")],
            [KeyboardButton(text="ЛДУБЖД"), KeyboardButton(text="ІТ Степ Університет")],
            [KeyboardButton(text="Інший")]
        ],
        resize_keyboard=True
    )
