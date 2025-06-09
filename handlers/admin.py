from aiogram import Router, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.exceptions import TelegramAPIError
from aiogram.types import ReplyKeyboardRemove, FSInputFile
from dotenv import load_dotenv
import asyncio
import os
import json
import zipfile
import aiohttp
from keyboards.main_menu_kb import main_menu_kb
from utils.database import get_all_users, cv_collection, db, count_all_users, get_user, get_cv, add_cv, update_cv_file_path
from PIL import Image, ImageDraw, ImageFont
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
ADMIN = os.getenv("ADMIN")

router = Router()

class BroadcastStates(StatesGroup):
    enter_broadcast_text = State()
    confirm_broadcast = State()

class FeedbackStates(StatesGroup):
    waiting_for_comment = State()

class AdminEditCVStates(StatesGroup):
    select_cv = State()
    select_field = State()
    edit_field = State()

def admin_inline_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📢 Розсилка всім користувачам", callback_data="broadcast")],
            [InlineKeyboardButton(text="📄 Отримати всі CV", callback_data="get_cvs")],
            [InlineKeyboardButton(text="📊 Запит на відгуки", callback_data="get_feedback")],
            [InlineKeyboardButton(text="💸 Розсилка збору", callback_data="zbir_broadcast")],
            [InlineKeyboardButton(text="👥 Кількість користувачів", callback_data="count_users")],
            [InlineKeyboardButton(text="📦 Завантажити ZIP з усіма CV", callback_data="download_cvs_zip")],
            [InlineKeyboardButton(text="📈 Покращити згенеровані CV", callback_data="improve_cvs")],
        ]
    )

def draw_wrapped_text(draw, text, font, fill, x, y, max_width_pixels, line_spacing=5):
    lines = []
    words = text.split()
    current_line = ""
    
    for word in words:
        test_line = f"{current_line} {word}".strip()
        bbox = font.getbbox(test_line)
        text_width = bbox[2] - bbox[0]
        
        if text_width <= max_width_pixels:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    
    if current_line:
        lines.append(current_line)
    
    line_height = font.getbbox("A")[3] - font.getbbox("A")[1] + line_spacing
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        y += line_height
    return y
import os
import json
import zipfile
from PIL import Image, ImageDraw, ImageFont
import logging
import aiohttp
from aiogram.types import FSInputFile

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def generate_improved_cv(user_id, temp_dir, cv_data):
    """
    Генерує покращене CV у форматі PDF для користувача з повними даними.
    """
    required_fields = ['position', 'languages', 'education', 'experience', 'skills', 'about', 'contacts']
    missing_fields = [field for field in required_fields if not cv_data.get(field)]
    user_name = cv_data.get("user_name", f"User_{user_id}")
    safe_user_name = "".join(c for c in user_name if c.isalnum() or c in ('_',)).replace(' ', '_')
    pdf_path = os.path.join(temp_dir, f"CV_{safe_user_name}_{user_id}.pdf")
    
    try:
        # Verify template and font files
        if not os.path.exists("templates/cv_template.png"):
            logger.error(f"Template file missing for user {user_id}: templates/cv_template.png")
            return None, None, missing_fields
        
        if not os.path.exists("fonts/Nunito-Regular.ttf") or not os.path.exists("fonts/Exo2-Regular.ttf"):
            logger.error(f"Font files missing for user {user_id}")
            return None, None, missing_fields
        
        image = Image.open("templates/cv_template.png").convert("RGB")
        draw = ImageDraw.Draw(image)
        font_text = ImageFont.truetype("fonts/Nunito-Regular.ttf", 16)
        font_title = ImageFont.truetype("fonts/Exo2-Regular.ttf", 40)
        
        max_width_pixels = 350
        x_position = 320
        y_position = 60
        
        y_position = draw_wrapped_text(
            draw, user_name, font=font_title, fill="#111A94", 
            x=x_position, y=y_position, max_width_pixels=max_width_pixels, line_spacing=10
        )
        y_position += 30
        
        fields = [
            ("Бажана посада:", cv_data.get('position')),
            ("Володіння мовами:", cv_data.get('languages')),
            ("Освіта:", cv_data.get('education')),
            ("Досвід:", cv_data.get('experience')),
            ("Навички:", cv_data.get('skills')),
            ("Про кандидата:", cv_data.get('about')),
            ("Контакти:", cv_data.get('contacts'))
        ]
        
        for label, content in fields:
            y_position = draw_wrapped_text(
                draw, label, font=font_text, fill="#111A94", 
                x=x_position, y=y_position, max_width_pixels=max_width_pixels, line_spacing=5
            )
            y_position += 10
            y_position = draw_wrapped_text(
                draw, content, font=font_text, fill="#000000", 
                x=x_position + 10, y=y_position, max_width_pixels=max_width_pixels - 10, line_spacing=5
            )
            y_position += 20
        
        image.save(pdf_path, "PDF")
        
        # Verify PDF file
        if not os.path.exists(pdf_path) or os.path.getsize(pdf_path) == 0:
            logger.error(f"Generated PDF for user {user_id} is empty or missing")
            return None, None, missing_fields
        if os.path.getsize(pdf_path) > 10 * 1024 * 1024:  # 10 MB limit
            logger.error(f"Generated PDF for user {user_id} exceeds 10 MB")
            return None, None, missing_fields
        
        return pdf_path, user_name, missing_fields
    except Exception as e:
        logger.error(f"Error generating CV for user {user_id}: {e}")
        return None, None, missing_fields

@router.callback_query(F.data == "improve_cvs")
async def improve_cvs_callback(callback: CallbackQuery):
    await callback.message.answer("📈 Створюємо покращені CV та формуємо ZIP-архіви...")
    
    temp_dir = "temp_cv_files"
    os.makedirs(temp_dir, exist_ok=True)
    improved_zip_path = os.path.join(temp_dir, "improved_cvs_archive.zip")
    incomplete_zip_path = os.path.join(temp_dir, "incomplete_cvs_archive.zip")
    improved_count = 0
    incomplete_count = 0
    failed_improved = 0
    failed_incomplete = 0
    
    cursor = cv_collection.find({})
    complete_cvs = []
    incomplete_cvs = []
    required_fields = ['position', 'languages', 'education', 'experience', 'skills', 'about', 'contacts']
    
    # Розподіляємо CV на повні та неповні
    async for cv in cursor:
        user_id = cv.get("telegram_id")
        if user_id:
            missing_fields = [field for field in required_fields if not cv.get(field)]
            if missing_fields:
                incomplete_cvs.append((user_id, cv))
            else:
                complete_cvs.append((user_id, cv))
    
    if not complete_cvs and not incomplete_cvs:
        await callback.message.answer("❌ Жодного CV не знайдено.")
        if os.path.exists(temp_dir):
            for file in os.listdir(temp_dir):
                os.remove(os.path.join(temp_dir, file))
            os.rmdir(temp_dir)
        return
    
    # Створюємо ZIP для покращених CV (лише повні)
    with zipfile.ZipFile(improved_zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for user_id, cv_data in complete_cvs:
            pdf_path, user_name, missing_fields = await generate_improved_cv(user_id, temp_dir, cv_data)
            safe_user_name = "".join(c for c in user_name if c.isalnum() or c in ('_',)).replace(' ', '_')
            
            if pdf_path:
                file_name = f"CV_{safe_user_name}.pdf"
                try:
                    zipf.write(pdf_path, file_name)
                    improved_count += 1
                    logger.info(f"Added improved CV for user {user_id} to ZIP")
                except Exception as e:
                    failed_improved += 1
                    logger.error(f"Failed to add improved CV for user {user_id} to ZIP: {e}")
                finally:
                    if os.path.exists(pdf_path):
                        try:
                            os.remove(pdf_path)
                            logger.info(f"Removed temporary PDF for user {user_id}")
                        except Exception as e:
                            logger.error(f"Error removing temp PDF for user {user_id}: {e}")
            else:
                failed_improved += 1
                logger.warning(f"Failed to generate improved CV for user {user_id}")
            
            await asyncio.sleep(0.1)  # Avoid rate limits
    
    # Створюємо ZIP для неповних CV (існуючі PDF)
    with zipfile.ZipFile(incomplete_zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        async with aiohttp.ClientSession() as session:
            for user_id, cv_data in incomplete_cvs:
                cv_file_path = cv_data.get("cv_file_path")
                user_name = cv_data.get("user_name", f"User_{user_id}")
                safe_user_name = "".join(c for c in user_name if c.isalnum() or c in ('_',)).replace(' ', '_')
                
                if cv_file_path:
                    try:
                        file_info = await callback.bot.get_file(cv_file_path)
                        file_url = f"https://api.telegram.org/file/bot{callback.bot.token}/{file_info.file_path}"
                        async with session.get(file_url) as response:
                            if response.status == 200:
                                file_data = await response.read()
                                file_name = f"CV_{safe_user_name}.pdf"
                                temp_file_path = os.path.join(temp_dir, file_name)
                                with open(temp_file_path, "wb") as f:
                                    f.write(file_data)
                                zipf.write(temp_file_path, file_name)
                                os.remove(temp_file_path)
                                incomplete_count += 1
                                logger.info(f"Added incomplete CV for user {user_id} to ZIP")
                            else:
                                failed_incomplete += 1
                                logger.warning(f"Failed to download incomplete CV for user {user_id}: HTTP {response.status}")
                    except Exception as e:
                        failed_incomplete += 1
                        logger.warning(f"Failed to process incomplete CV for user {user_id}: {e}")
                else:
                    failed_incomplete += 1
                    logger.warning(f"No CV file found for incomplete CV of user {user_id}")
                
                await asyncio.sleep(0.1)  # Avoid rate limits
    
    # Відправляємо архів із покращеними CV
    if improved_count > 0:
        try:
            zip_file = FSInputFile(improved_zip_path, filename="improved_cvs_archive.zip")
            await callback.message.answer_document(
                document=zip_file,
                caption=f"✅ ZIP-архів із {improved_count} покращених CV (повні дані) створено.\n"
                        f"Помилки: {failed_improved}"
            )
        except Exception as e:
            await callback.message.answer(f"❌ Помилка при відправці архіву покращених CV: {e}")
    else:
        await callback.message.answer(f"❌ Жодного покращеного CV не створено. Помилки: {failed_improved}")
    
    # Відправляємо архів із неповними CV
    if incomplete_count > 0:
        try:
            zip_file = FSInputFile(incomplete_zip_path, filename="incomplete_cvs_archive.zip")
            await callback.message.answer_document(
                document=zip_file,
                caption=f"✅ ZIP-архів із {incomplete_count} неповних CV створено.\n"
                        f"Помилки: {failed_incomplete}"
            )
        except Exception as e:
            await callback.message.answer(f"❌ Помилка при відправці архіву неповних CV: {e}")
    else:
        await callback.message.answer(f"❌ Жодного неповного CV не додано до архіву. Помилки: {failed_incomplete}")
    
    # Очищення тимчасових файлів
    if os.path.exists(improved_zip_path):
        os.remove(improved_zip_path)
    if os.path.exists(incomplete_zip_path):
        os.remove(incomplete_zip_path)
    if os.path.exists(temp_dir):
        for file in os.listdir(temp_dir):
            os.remove(os.path.join(temp_dir, file))
        os.rmdir(temp_dir)

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
        "👋 Привіт, адміністраторе! Обери опцію:",
        reply_markup=admin_inline_kb()
    )

@router.callback_query(F.data == "count_users")
async def count_users_callback(callback: CallbackQuery):
    count = await count_all_users()
    await callback.message.answer(f"👥 Зареєстрованих користувачів: {count}")

@router.callback_query(F.data == "broadcast")
async def broadcast_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "📝 Введіть текст повідомлення для розсилки. "
        "Для додавання фото надішліть його з текстом у підписі."
    )
    await state.set_state(BroadcastStates.enter_broadcast_text)

@router.message(BroadcastStates.enter_broadcast_text, F.content_type.in_({"text", "photo"}))
async def enter_broadcast_text(message: Message, state: FSMContext):
    text_to_broadcast = message.caption or message.text or ""
    photo_id = message.photo[-1].file_id if message.photo else None

    await state.update_data(broadcast_text=text_to_broadcast, photo_id=photo_id)

    preview_text = f"📢 Повідомлення для розсилки:\n\n{text_to_broadcast or 'Без тексту'}\n\nПідтверджуєте розсилку?"
    
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
        if user.get("telegram_id"):
            user_ids.append(user["telegram_id"])

    if not user_ids:
        await callback.message.answer("❌ Помилка: Не знайдено жодного користувача для розсилки.")
        await state.clear()
        return

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
            logger.warning(f"Помилка відправки до {user_id}: {e}")
        await asyncio.sleep(0.05)  # Telegram rate limit

    await callback.message.answer(
        f"📢 Розсилку завершено!\n✅ Успішно: {success}\n❌ Помилки: {fail}"
    )
    await state.clear()

@router.callback_query(F.data == "cancel_broadcast", BroadcastStates.confirm_broadcast)
async def cancel_broadcast(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("❌ Розсилку скасовано.")
    await state.clear()

def format_cv_text(cv_text) -> str:
    if isinstance(cv_text, str):
        try:
            cv_text = json.loads(cv_text)
        except json.JSONDecodeError:
            return f"<i>Невірний формат CV:</i> {cv_text}"

    formatted = ""
    for key, value in cv_text.items():
        title = key.replace('_', ' ').capitalize()
        formatted += f"<b>{title}:</b> {value}\n"
    return formatted.strip()

@router.callback_query(F.data == "get_cvs")
async def get_cvs_callback(callback: CallbackQuery):
    await callback.message.answer("📄 Збираю всі CV користувачів...")

    cursor = cv_collection.find({})
    count = 0
    async for cv in cursor:
        user_id = cv.get("telegram_id")
        cv_file_path = cv.get("cv_file_path")

        if cv_file_path:
            try:
                file_info = await callback.bot.get_file(cv_file_path)
                file_url = f"https://api.telegram.org/file/bot{callback.bot.token}/{file_info.file_path}"

                await callback.message.answer(
                    f"<b>Користувач ID:</b> <code>{user_id}</code>\n"
                    f"<b>Ім'я:</b> {cv.get('user_name')}\n"
                    f"📎 <b>CV:</b> <a href='{file_url}'>Завантажити файл</a>",
                    parse_mode="HTML",
                    disable_web_page_preview=True
                )
            except Exception as e:
                await callback.message.answer(
                    f"❌ Не вдалося отримати CV для користувача {user_id}.\nПомилка: <code>{e}</code>",
                    parse_mode="HTML"
                )
        else:
            await callback.message.answer(
                f"❌ CV відсутнє для користувача {user_id}.",
                parse_mode="HTML"
            )
        count += 1

    if count == 0:
        await callback.message.answer("❌ Жодного CV не знайдено.")
    else:
        await callback.message.answer(f"✅ Опрацьовано {count} CV.")

def rating_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⭐ 1 – Не сподобалось", callback_data="rate_1")],
            [InlineKeyboardButton(text="⭐ 2 – Могло бути краще", callback_data="rate_2")],
            [InlineKeyboardButton(text="⭐ 3 – Було нормально", callback_data="rate_3")],
            [InlineKeyboardButton(text="⭐ 4 – Було круто!", callback_data="rate_4")],
            [InlineKeyboardButton(text="⭐ 5 – Неймовірно!", callback_data="rate_5")],
        ]
    )

@router.callback_query(F.data == "get_feedback")
async def broadcast_feedback_request(callback: CallbackQuery):
    confirm_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Так, розіслати", callback_data="confirm_feedback_request")],
            [InlineKeyboardButton(text="❌ Ні, скасувати", callback_data="cancel_feedback_request")]
        ]
    )
    await callback.message.answer(
        "📊 Ви впевнені, що хочете розіслати запит на фідбек?",
        reply_markup=confirm_kb
    )

@router.callback_query(F.data == "confirm_feedback_request")
async def send_feedback_request(callback: CallbackQuery):
    users_cursor = await get_all_users()
    user_ids = []
    async for user in users_cursor:
        if user.get("telegram_id"):
            user_ids.append(user["telegram_id"])

    if not user_ids:
        await callback.message.answer("❌ Помилка: Не знайдено жодного користувача для розсилки.")
        return

    success = 0
    fail = 0
    for user_id in user_ids:
        try:
            await callback.bot.send_message(
                user_id,
                "📊 Оціни <b>Інженерний Ярмарок Карʼєри</b> від 1 до 5!",
                parse_mode="HTML",
                reply_markup=rating_keyboard()
            )
            success += 1
        except TelegramAPIError as e:
            fail += 1
            logger.warning(f"Помилка відправки до {user_id}: {e}")
        await asyncio.sleep(0.05)

    await callback.message.answer(f"✅ Запит на фідбек розіслано!\nУспішно: {success}\nПомилки: {fail}")

@router.callback_query(F.data == "cancel_feedback_request")
async def cancel_feedback_request(callback: CallbackQuery):
    await callback.message.answer("❌ Запит на фідбек скасовано.")

@router.callback_query(F.data.startswith("rate_"))
async def handle_rating(callback: CallbackQuery, state: FSMContext):
    rating = int(callback.data.split("_")[1])
    await state.update_data(rating=rating)
    await callback.message.edit_text(
        "🙏 Дякуємо за оцінку! Напиши, що сподобалось, а що можна покращити.",
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
        {"$set": {"telegram_id": user_id, "rating": rating, "comment": comment}},
        upsert=True
    )

    await message.answer(
        "🙌 Дякуємо за відгук! Слідкуй за <b>BEST Lviv</b> для нових подій!",
        parse_mode="HTML",
        reply_markup=main_menu_kb()
    )
    await state.clear()

@router.callback_query(F.data == "zbir_broadcast")
async def zbir_broadcast_prompt(callback: CallbackQuery):
    confirm_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Так, розіслати", callback_data="confirm_zbir_broadcast")],
            [InlineKeyboardButton(text="❌ Ні, скасувати", callback_data="cancel_zbir_broadcast")]
        ]
    )
    photo_path = "media/zbir.jpg"
    preview_caption = (
        "💸 <b>Збір на підтримку медиків 67 ОМБ</b>\n\n"
        "Збираємо на протидронові сітки для евак авто.\n"
        "🎯 Ціль: 15 000 ₴\n"
        "🔗 <a href='https://send.monobank.ua/jar/87vmuFGKQL'>Посилання на збір</a>\n"
        "🎁 Кожні 50 грн – шанс виграти подарунок!\n"
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
        "💸 <b>Збір на підтримку медиків 67 ОМБ</b>\n\n"
        "Збираємо на протидронові сітки для евак авто.\n"
        "🎯 Ціль: 15 000 ₴\n"
        "🔗 <a href='https://send.monobank.ua/jar/87vmuFGKQL'>Посилання на збір</a>\n"
        "🎁 Кожні 50 грн – шанс виграти подарунок!\n"
        "<span class='tg-spoiler'>Долучайся 💙</span>"
    )

    users_cursor = await get_all_users()
    user_ids = []
    async for user in users_cursor:
        if user.get("telegram_id"):
            user_ids.append(user["telegram_id"])

    if not user_ids:
        await callback.message.answer("❌ Помилка: Не знайдено жодного користувача для розсилки.")
        return

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
            logger.warning(f"Помилка відправки до {user_id}: {e}")
        await asyncio.sleep(0.05)

    await callback.message.answer(f"✅ Повідомлення зі збором розіслано!\nУспішно: {success}\nПомилки: {fail}")

@router.callback_query(F.data == "cancel_zbir_broadcast")
async def cancel_zbir_broadcast(callback: CallbackQuery):
    await callback.message.answer("❌ Розсилку збору скасовано.")

@router.callback_query(F.data == "download_cvs_zip")
async def download_cvs_zip(callback: CallbackQuery):
    await callback.message.answer("📦 Збираю всі CV у ZIP-архів...")

    cursor = cv_collection.find({})
    temp_dir = "temp_cv_files"
    os.makedirs(temp_dir, exist_ok=True)
    zip_path = os.path.join(temp_dir, "cvs_archive.zip")
    count = 0
    failed = 0

    async with aiohttp.ClientSession() as session:
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            async for cv in cursor:
                user_id = cv.get("telegram_id")
                cv_file_path = cv.get("cv_file_path")
                user_name = cv.get("user_name", f"user_{user_id}")

                if cv_file_path:
                    try:
                        file_info = await callback.bot.get_file(cv_file_path)
                        file_url = f"https://api.telegram.org/file/bot{callback.bot.token}/{file_info.file_path}"
                        async with session.get(file_url) as response:
                            if response.status == 200:
                                file_data = await response.read()
                                safe_user_name = "".join(c for c in user_name if c.isalnum() or c in (' ', '_')).replace(' ', '_')
                                file_name = f"cv_{safe_user_name}_{user_id}.pdf"
                                temp_file_path = os.path.join(temp_dir, file_name)
                                with open(temp_file_path, "wb") as f:
                                    f.write(file_data)
                                zipf.write(temp_file_path, file_name)
                                os.remove(temp_file_path)
                                count += 1
                            else:
                                failed += 1
                                logger.warning(f"Не вдалося завантажити файл для користувача {user_id}: HTTP {response.status}")
                    except Exception as e:
                        failed += 1
                        logger.warning(f"Помилка обробки CV для користувача {user_id}: {e}")
                else:
                    failed += 1
                    logger.warning(f"CV відсутнє для користувача {user_id}")

    if count == 0:
        await callback.message.answer("❌ Жодного CV не знайдено.")
        if os.path.exists(temp_dir):
            for file in os.listdir(temp_dir):
                os.remove(os.path.join(temp_dir, file))
            os.rmdir(temp_dir)
        return

    try:
        zip_file = FSInputFile(zip_path, filename="cvs_archive.zip")
        await callback.message.answer_document(
            document=zip_file,
            caption=f"✅ ZIP-архів з {count} CV створено. Помилки: {failed}"
        )
    except Exception as e:
        await callback.message.answer(f"❌ Помилка при відправці ZIP-архіву: {e}")
    finally:
        if os.path.exists(zip_path):
            os.remove(zip_path)
        if os.path.exists(temp_dir):
            for file in os.listdir(temp_dir):
                os.remove(os.path.join(temp_dir, file))
            os.rmdir(temp_dir)