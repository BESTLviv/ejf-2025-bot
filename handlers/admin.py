from aiogram import Router, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.exceptions import TelegramAPIError
from dotenv import load_dotenv
import asyncio
import os
import json
from aiogram.types import ReplyKeyboardRemove, FSInputFile
from keyboards.main_menu_kb import main_menu_kb 
from utils.database import get_all_users, cv_collection, db, count_all_users 

load_dotenv()
ADMIN = os.getenv("ADMIN")

router = Router()

class BroadcastStates(StatesGroup):
    enter_broadcast_text = State()
    confirm_broadcast = State()

class FeedbackStates(StatesGroup):
    waiting_for_comment = State()

def admin_inline_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Розсилка всім користувачам", callback_data="broadcast")],
            [InlineKeyboardButton(text="Отримати всі CV користувачів", callback_data="get_cvs")],
            [InlineKeyboardButton(text="Розсилка для відгуків", callback_data="get_feedback")],
            [InlineKeyboardButton(text="Розсилка збору", callback_data="zbir_brodcast")],
            [InlineKeyboardButton(text="Кількість зареєстрованих користувачів", callback_data="count_users")],
        ]
    )

@router.callback_query(F.data == "count_users")
async def count_users_callback(callback: CallbackQuery):
    count = await count_all_users()
    await callback.message.answer(f"✅ Кількість зареєстрованих користувачів: {count}")

def confirm_broadcast_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Так, розіслати", callback_data="confirm_broadcast")],
            [InlineKeyboardButton(text="❌ Ні, скасувати", callback_data="cancel_broadcast")],
        ]
    )

@router.message(F.text == ADMIN)
async def admin_message_handler(message: Message):
    await message.answer(
        "Привіт, адміністратор-молодчинка! Ось твої опції:",
        reply_markup=admin_inline_kb()
    )

@router.callback_query(F.data == "broadcast")
async def broadcast_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "Будь ласка, введіть текст повідомлення для розсилки. "
        "Якщо хочете додати фото, надішліть його разом із текстом у підписі."
    )
    await state.set_state(BroadcastStates.enter_broadcast_text)

@router.message(BroadcastStates.enter_broadcast_text, F.content_type.in_({"text", "photo"}))
async def enter_broadcast_text(message: Message, state: FSMContext):
    
    text_to_broadcast = message.caption or message.text or ""
    photo_id = message.photo[-1].file_id if message.photo else None

    await state.update_data(broadcast_text=text_to_broadcast, photo_id=photo_id)

    preview_text = f"Ось ваше повідомлення для розсилки:\n\n{text_to_broadcast or 'Без тексту'}\n\nВи підтверджуєте розсилку цього повідомлення всім користувачам?"
    
    if photo_id:
        await message.answer_photo(
            photo=photo_id,
            caption=preview_text,
            reply_markup=confirm_broadcast_kb(),
            parse_mode="HTML"
        )
    else:
        await message.answer(
            preview_text,
            reply_markup=confirm_broadcast_kb(),
            parse_mode="HTML"
        )

    await state.set_state(BroadcastStates.confirm_broadcast)

@router.callback_query(F.data == "confirm_broadcast", BroadcastStates.confirm_broadcast)
async def confirm_broadcast(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    text_to_broadcast = data.get("broadcast_text", "")
    photo_id = data.get("photo_id")

    users_cursor = await get_all_users()
    user_ids = []
    async for user in users_cursor:
        if user.get("registered"):
            user_ids.append(user["telegram_id"])

    success = 0
    fail = 0
    for user_id in user_ids:
        try:
            if photo_id:
                await callback.bot.send_photo(
                    chat_id=user_id,
                    photo=photo_id,
                    caption=text_to_broadcast,
                    parse_mode="HTML"
                )
            else:
                await callback.bot.send_message(
                    chat_id=user_id,
                    text=text_to_broadcast,
                    parse_mode="HTML"
                )
            success += 1
        except TelegramAPIError as e:
            fail += 1
            print(f"Помилка відправки до {user_id}: {e}")
        await asyncio.sleep(0.05)

    await callback.message.answer(
        f"Розсилку завершено!\n✅ Успішно: {success}\n❌ Помилки: {fail}"
    )
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

def rating_keyboard():
    keyboard = [
        [InlineKeyboardButton(text=f"⭐ 1 – Не сподобалось", callback_data="rate_1")],
        [InlineKeyboardButton(text=f"⭐ 2 – Могло бути краще", callback_data="rate_2")],
        [InlineKeyboardButton(text=f"⭐ 3 – Було нормально", callback_data="rate_3")],
        [InlineKeyboardButton(text=f"⭐ 4 – Було круто!", callback_data="rate_4")],
        [InlineKeyboardButton(text=f"⭐ 5 – Неймовірно, чекаю наступний ІЯК!", callback_data="rate_5")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

@router.callback_query(F.data == "get_feedback")
async def broadcast_feedback_request(callback: CallbackQuery):
    confirm_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Так, розіслати", callback_data="confirm_feedback_request")],
        [InlineKeyboardButton(text="❌ Ні, скасувати", callback_data="cancel_feedback_request")]
    ])
    await callback.message.answer(
        "Ви впевнені, що хочете розіслати запит на фідбек всім користувачам?",
        reply_markup=confirm_kb
    )

@router.callback_query(F.data == "confirm_feedback_request")
async def send_feedback_request(callback: CallbackQuery):
    await callback.message.answer("Розсилка запитів на фідбек користувачам...")

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
                "Це були два неймовірні дні! Ми намагалися зробити <b>Інженерний Ярмарок Карʼєри</b> якомога кориснішим і цікавишим для тебе. А тепер твоя черга допомогти нам стати кращими! Оціни, будь ласка, захід від 1 до 5 📊.",
                parse_mode="HTML",
                reply_markup=rating_keyboard()
            )
            success += 1
        except TelegramAPIError:
            fail += 1
            await asyncio.sleep(0.05)

    await callback.message.answer(f"✅ Запит на фідбек розіслано!\nУспішно: {success}\nПомилки: {fail}")

@router.callback_query(F.data == "cancel_feedback_request")
async def cancel_feedback_request(callback: CallbackQuery):
    await callback.message.answer("❌ Розсилку запитів на фідбек скасовано.")

@router.callback_query(F.data.startswith("rate_"))
async def handle_rating(callback: CallbackQuery, state: FSMContext):
    rating = int(callback.data.split("_")[1])
    await state.update_data(rating=rating)
    await callback.message.edit_text(
        f"🙏 Дякуємо за оцінку!\n Нам дуже важливо почути твою думку. Напиши, що тобі сподобалось, а що можна покращити, адже саме твій відгук спонукає нас до розвитку!",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(FeedbackStates.waiting_for_comment)

@router.message(FeedbackStates.waiting_for_comment)
async def save_feedback(message: Message, state: FSMContext):
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

    await message.answer(
        "Дуже дякуємо! Твої відповіді допоможуть нам рухатися у правильному напрямку.\n\n"
        "Хочемо нагадати, що <b>Інженерний Ярмарок Кар’єри</b> став можливим завдяки студентській організації <b>BEST Lviv</b>. "
        "Ми створюємо й інші круті події, які можуть тебе зацікавити: \n\n"
        "🟣 <b>BEST Training Week</b> – тиждень лекцій від спікерів;\n"
        "🔴 <b>BEST Capture The Flag</b> – командні змагання з кібербезпеки;\n"
        "🟠 <b>BEST Engineering Competition</b> – інженерні змагання;\n"
        "🟢 <b>BEST::HACKath0n</b> – 24-годинні IT-змагання;\n"
        "Усі ці заходи є <b>безкоштовними</b>, тож слідкуй за нашими соцмережами та долучайся до інших подій, які зацікавили! 🎯",
        parse_mode="HTML",
        reply_markup=main_menu_kb()
    )
    await state.clear()

@router.callback_query(F.data == "zbir_brodcast")
async def zbir_broadcast_prompt(callback: CallbackQuery):
    confirm_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Так, розіслати", callback_data="confirm_zbir_broadcast")],
        [InlineKeyboardButton(text="❌ Ні, скасувати", callback_data="cancel_zbir_broadcast")]
    ])

    photo_path = "media/zbir.jpg"
    preview_caption = (
        "Інженерний Ярмарок Карʼєри приєднується до збору <b>на підтримку медиків 67 ОМБ.</b>\n\n"
        "Збираємо на протидронові сітки для евак авто в межах збору від БФ \"Вдячні\" | BEST Lviv\n\n"
        "🎯 Ціль: 15 000 ₴\n\n"
        "🔗Посилання на збір\nhttps://send.monobank.ua/jar/87vmuFGKQL\n\n"
        "🎁Кожні 50 грн – шанс виграти подарунок.\n\n"
        "Кожен ваш донат - це серце, що битиметься далі.\n"
        "<span class='tg-spoiler'>Долучайся 💙</span>"
    )
    photo = FSInputFile(photo_path)
    await callback.message.answer_photo(
        photo=photo,
        caption=preview_caption,
        parse_mode="HTML",
        reply_markup=confirm_kb
    )

@router.callback_query(F.data == "confirm_zbir_broadcast")
async def confirm_zbir_broadcast(callback: CallbackQuery):
    photo_path = "media/zbir.jpg"
    caption = (
        "Інженерний Ярмарок Карʼєри приєднується до збору <b>на підтримку медиків 67 ОМБ.</b>\n\n"
        "Збираємо на протидронові сітки для евак авто в межах збору від БФ \"Вдячні\" | BEST Lviv\n\n"
        "🎯 Ціль: 15 000 ₴\n\n"
        "🔗Посилання на збір\nhttps://send.monobank.ua/jar/87vmuFGKQL\n\n"
        "🎁Кожні 50 грн – шанс виграти подарунок.\n\n"
        "Кожен ваш донат - це серце, що битиметься далі.\n"
        "<span class='tg-spoiler'>Долучайся 💙</span>"
    )

    users_cursor = await get_all_users()
    user_ids = []
    async for user in users_cursor:
        if user.get("registered"):
            user_ids.append(user["telegram_id"])

    success = 0
    fail = 0
    photo = FSInputFile(photo_path)
    for user_id in user_ids:
        try:
            await callback.bot.send_photo(
                chat_id=user_id,
                photo=photo,
                caption=caption,
                parse_mode="HTML"
            )
            success += 1
        except TelegramAPIError as e:
            fail += 1
            print(f"Помилка відправки до {user_id}: {e}")
            await asyncio.sleep(0.05)

    await callback.message.answer(f"✅ Повідомлення зі збором розіслано!\nУспішно: {success}\nПомилки: {fail}")

@router.callback_query(F.data == "cancel_zbir_broadcast")
async def cancel_zbir_broadcast(callback: CallbackQuery):
    await callback.message.answer("❌ Розсилку повідомлення зі збором скасовано.")