from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram import F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

router = Router()

def main_menu_kb():
    return InlineKeyboardMarkup(
        row_width=2,  
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📅 Розклад", callback_data="schedule"),
                InlineKeyboardButton(text="📂 CV", callback_data="cv"),
            ],
            [
                InlineKeyboardButton(text="🎯 Гра Share and Win", callback_data="game"),
                InlineKeyboardButton(text="🗣️ Спікери", callback_data="speakers"),
            ],
            [
                InlineKeyboardButton(text="🩵💛 Підтримка ЗСУ", callback_data="support_ukraine"),
            ]
        ]
    )

@router.message(F.text == "Старт 🚀")
async def start_registration(message: types.Message, state: FSMContext):
    await message.answer(
        "📢 Інженерний Ярмарок Кар’єри — це місце, де ти зможеш познайомитися з топовими компаніями, дізнатись про вакансії, а також взяти участь у цікавих активностях.\n"
        "Тепер, познайомимося ближче!",
        reply_markup=main_menu_kb() 
    )
    await message.answer(
        "Зараз на панелі ти бачиш розділи – тисни на них, щоб дізнатись більше деталей про кожен блок 🔎.",
        reply_markup=main_menu_kb()
    )


@router.callback_query(F.data == "schedule")
async def show_schedule(callback_query: types.CallbackQuery):
    await callback_query.answer("Тут буде інформація про розклад подій Ярмарку. Очікуйте оновлення! 🎤")
    await callback_query.message.edit_reply_markup(reply_markup=None)

@router.callback_query(F.data == "cv")
async def show_cv(callback_query: types.CallbackQuery):
    await callback_query.answer("Завантажте своє резюме або створіть його за допомогою бота. Що ви хочете зробити? 📄")
    await callback_query.message.edit_reply_markup(reply_markup=None)

@router.callback_query(F.data == "game")
async def share_and_win(callback_query: types.CallbackQuery):
    await callback_query.answer("Гра для учасників Ярмарку: Share and Win! Тисни кнопку нижче, щоб дізнатись більше! 🎉")
    await callback_query.message.edit_reply_markup(reply_markup=None)

@router.callback_query(F.data == "speakers")
async def show_speakers(callback_query: types.CallbackQuery):
    await callback_query.answer("Тут буде список спікерів на Ярмарку. Бажаєте дізнатись більше про спікерів? 👨‍🏫")
    await callback_query.message.edit_reply_markup(reply_markup=None)

@router.callback_query(F.data == "support_ukraine")
async def show_ukraine_support(callback_query: types.CallbackQuery):
    await callback_query.answer("У цьому розділі буде інформація про допомогу ЗСУ. Давайте разом підтримувати наших героїв! 🇺🇦")
    await callback_query.message.edit_reply_markup(reply_markup=None)

@router.message()
async def handle_unknown_message(message: types.Message):
    await message.answer("Вибачте, я не розумію цього запиту. Спробуйте вибрати один з розділів меню.")
