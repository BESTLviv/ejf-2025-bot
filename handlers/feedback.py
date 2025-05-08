from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from motor.motor_asyncio import AsyncIOMotorDatabase
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

router = Router()

class FeedbackStates(StatesGroup):
    waiting_for_comment = State()

def rating_keyboard():
    keyboard = [
        [InlineKeyboardButton(text=f"{i} ⭐", callback_data=f"rate_{i}")] for i in range(1, 6)
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

@router.message(F.text == "Залишити відгук")
async def ask_rating(message: Message):
    await message.answer(
        "Оціни, будь ласка, подію від 1 до 5 ⭐️",
        reply_markup=rating_keyboard()
    )

@router.callback_query(F.data.startswith("rate_"))
async def handle_rating(callback: CallbackQuery, state: FSMContext, db: AsyncIOMotorDatabase):
    user_id = callback.from_user.id
    rating = int(callback.data.split("_")[1])

    await state.update_data(rating=rating)

    await callback.message.edit_text(f"Твоя оцінка: {rating} ⭐️\nТепер напиши короткий відгук ✍️")
    await state.set_state(FeedbackStates.waiting_for_comment)


@router.message(FeedbackStates.waiting_for_comment)
async def save_feedback(message: Message, state: FSMContext, db: AsyncIOMotorDatabase):
    user_id = message.from_user.id
    comment = message.text

    data = await state.get_data()
    rating = data.get('rating')

    feedback_collection = db["feedback"]
    await feedback_collection.update_one(
        {"telegram_id": user_id},
        {"$set": {
            "rating": rating,
            "comment": comment
        }},
        upsert=True
    )

    await message.answer("Дякуємо за детальний відгук! 💙💛")
    await state.clear()
