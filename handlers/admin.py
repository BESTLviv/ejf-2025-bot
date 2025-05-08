from aiogram import Router, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.exceptions import TelegramAPIError
from dotenv import load_dotenv
import asyncio
import os
import json

from utils.database import get_all_users, cv_collection, db  # додаємо db для підключення до feedbacks

load_dotenv()
ADMIN = os.getenv("ADMIN")

router = Router()

class BroadcastStates(StatesGroup):
    enter_broadcast_text = State()
    confirm_broadcast = State()

def admin_inline_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Розсилка всім користувачам", callback_data="broadcast")],
            [InlineKeyboardButton(text="Отримати всі CV користувачів", callback_data="get_cvs")],
            [InlineKeyboardButton(text="Розсилка для відгуків", callback_data="get_feedback")],
        ]
    )

def confirm_broadcast_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Так, розіслати", callback_data="confirm_broadcast")],
            [InlineKeyboardButton(text="❌ Ні, скасувати", callback_data="cancel_broadcast")],
        ]
    )

@router.message(F.text == ADMIN)
async def admin_message_handler(message: types.Message):
    await message.answer(
        "Привіт, адміністратор-молодчинка! Ось твої опції:",
        reply_markup=admin_inline_kb()
    )

@router.callback_query(F.data == "broadcast")
async def broadcast_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Будь ласка, введіть текст повідомлення для розсилки (підтримується HTML):")
    await state.set_state(BroadcastStates.enter_broadcast_text)

@router.message(BroadcastStates.enter_broadcast_text)
async def enter_broadcast_text(message: types.Message, state: FSMContext):
    text_to_broadcast = message.html_text  
    await state.update_data(broadcast_text=text_to_broadcast)

    await message.answer(
        f"Ось текст вашої розсилки:\n\n{text_to_broadcast}\n\nВи підтверджуєте розсилку цього повідомлення всім користувачам?",
        reply_markup=confirm_broadcast_kb()
    )
    await state.set_state(BroadcastStates.confirm_broadcast)

@router.callback_query(F.data == "confirm_broadcast", BroadcastStates.confirm_broadcast)
async def confirm_broadcast(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    text_to_broadcast = data.get("broadcast_text")

    users_cursor = await get_all_users()
    user_ids = []
    async for user in users_cursor:
        if user.get("registered"):  
            user_ids.append(user["telegram_id"])

    success = 0
    fail = 0
    for user_id in user_ids:
        try:
            await callback.bot.send_message(user_id, text_to_broadcast, parse_mode="HTML")
            success += 1
        except TelegramAPIError as e: 
            fail += 1
            await asyncio.sleep(0.1) 


    await callback.message.answer(f"Розсилку завершено!\n✅ Успішно: {success}\n❌ Помилки: {fail}")
    await state.clear()

@router.callback_query(F.data == "cancel_broadcast", BroadcastStates.confirm_broadcast)
async def cancel_broadcast(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Розсилку скасовано.")
    await state.clear()


def format_cv_text(cv_text) -> str:
    if isinstance(cv_text, str):
        try:
            cv_text = json.loads(cv_text)
        except Exception:
            return f"<i>Невірний формат CV:</i> {cv_text}"

    formatted = ""
    for key, value in cv_text.items():
        title = key.replace('_', ' ').capitalize()
        formatted += f"<b>{title}:</b> {value}\n"
    return formatted.strip()

@router.callback_query(F.data == "get_cvs")
async def get_cvs_callback(callback: CallbackQuery):
    await callback.message.answer("Збираю всі CV користувачів...")

    cursor = cv_collection.find({})
    count = 0

    for cv in await cursor.to_list(length=None):
        user_id = cv.get("user_id")
        cv_file_path = cv.get("cv_file_path")

        if cv_file_path:
            try:
                file_info = await callback.bot.get_file(cv_file_path)
                file_url = f"https://api.telegram.org/file/bot{callback.bot.token}/{file_info.file_path}"

                await callback.message.answer(
                    f"<b>Користувач ID:</b> <code>{cv.get('telegram_id')}</code>\n"
                    f"<b>Ім'я користувача:</b> {cv.get('user_name')}\n"
                    f"📎 <b>CV:</b> <a href='{file_url}'>Завантажити файл</a>",
                    parse_mode="HTML",
                    disable_web_page_preview=True)

            except Exception as e:
                await callback.message.answer(
                    f"❌ Не вдалося створити посилання на CV для користувача {user_id}.\n"
                    f"Помилка: <code>{e}</code>",
                    parse_mode="HTML"
                )
        else:
            await callback.message.answer(
                f"❌ CV відсутнє для користувача {user_id}.",
                parse_mode="HTML"
            )

        count += 1

    if count == 0:
        await callback.message.answer("❌ Жодного CV користувачів не знайдено.")
    else:
        await callback.message.answer(f"✅ Завершено. Опрацьовано {count} CV.")




class FeedbackStates(StatesGroup):
    waiting_for_comment = State()


def rating_keyboard():
    keyboard = [
        [InlineKeyboardButton(text=f"{i} ⭐", callback_data=f"rate_{i}")] for i in range(1, 6)
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

@router.callback_query(F.data == "get_feedback")
async def broadcast_feedback_request(callback: CallbackQuery):
    await callback.message.answer("Розсилаю запит на фідбек всім користувачам...")

    users_cursor = await get_all_users()
    user_ids = []
    async for user in users_cursor:
        if user.get("registered"):  
            user_ids.append(user["telegram_id"])

    success = 0
    fail = 0
    for user_id in user_ids:
        try:
            await callback.bot.send_message(
                user_id,
                "Будь ласка, оціни подію від 1 до 5 ⭐️",
                reply_markup=rating_keyboard()
            )
            success += 1
        except TelegramAPIError:
            fail += 1
            await asyncio.sleep(0.1)

    await callback.message.answer(f"✅ Запит на фідбек розіслано!\nУспішно: {success}\nПомилки: {fail}")

@router.callback_query(F.data.startswith("rate_"))
async def handle_rating(callback: CallbackQuery, state: FSMContext):
    rating = int(callback.data.split("_")[1])

    await state.update_data(rating=rating)

    await callback.message.edit_text(f"Твоя оцінка: {rating} ⭐️\nТепер напиши короткий відгук ✍️")
    await state.set_state(FeedbackStates.waiting_for_comment)

@router.message(FeedbackStates.waiting_for_comment)
async def save_feedback(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    comment = message.text

    data = await state.get_data()
    rating = data.get('rating')

    feedback_collection = db["feedbacks"]
    await feedback_collection.update_one(
        {"telegram_id": user_id},
        {"$set": {
            "telegram_id": user_id,
            "rating": rating,
            "comment": comment
        }},
        upsert=True
    )

    await message.answer("Дякуємо за детальний відгук! 💙💛")
    await state.clear()
