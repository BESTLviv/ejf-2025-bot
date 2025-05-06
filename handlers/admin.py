from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from dotenv import load_dotenv
from aiogram.types.input_file import FSInputFile 
import os

from utils.database import get_all_users

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
        ]
    )

def confirm_broadcast_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Так, розіслати", callback_data="confirm_broadcast")],
            [InlineKeyboardButton(text="❌ Ні, скасувати", callback_data="cancel_broadcast")],
        ]
    )

# --- Хендлери ---
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
        except Exception as e:
            fail += 1

    await callback.message.answer(f"Розсилку завершено!\n✅ Успішно: {success}\n❌ Помилки: {fail}")
    await state.clear()

@router.callback_query(F.data == "cancel_broadcast", BroadcastStates.confirm_broadcast)
async def cancel_broadcast(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Розсилку скасовано.")
    await state.clear()

from utils.database import cv_collection
import os
@router.callback_query(F.data == "get_cvs")
async def get_cvs_callback(callback: CallbackQuery):
    await callback.message.answer("Збираю всі CV користувачів...")

    cursor = cv_collection.find({})
    count = 0
    async for cv in cursor:
        user_id = cv.get("user_id")
        cv_text = cv.get("cv_text")
        cv_file_id = cv.get("cv_file_id")  

        if cv_text:
            await callback.message.answer(
                f"<b>Користувач ID:</b> <code>{user_id}</code>\n"
                f"<b>Текстове CV:</b>\n{cv_text}",
                parse_mode="HTML"
            )
        else:
            await callback.message.answer(
                f"<b>Користувач ID:</b> <code>{user_id}</code>\n"
                f"❌ <i>Текстового CV немає</i>",
                parse_mode="HTML"
            )

        if cv_file_id:
            try:
                await callback.message.answer_document(cv_file_id, caption=f"📄 PDF CV користувача {user_id}")
            except Exception as e:
                await callback.message.answer(
                    f"❌ Не вдалося надіслати PDF CV для користувача {user_id}.\nПомилка: <code>{e}</code>",
                    parse_mode="HTML"
                )
        else:
            await callback.message.answer(
                f"❌ PDF CV відсутнє для користувача {user_id}.",
                parse_mode="HTML"
            )

        count += 1

    if count == 0:
        await callback.message.answer("❌ Жодного CV користувачів не знайдено.")
    else:
        await callback.message.answer(f"✅ Завершено. Опрацьовано {count} CV.")