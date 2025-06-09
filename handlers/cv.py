from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, BufferedInputFile
from aiogram.fsm.state import State, StatesGroup
from utils.database import get_user, add_cv, get_cv
from keyboards.cv_kb import get_cv_type_kb, change_cv_type_kb, has_cv_kb, back2menu_kb
from keyboards.main_menu_kb import main_menu_kb
from PIL import Image, ImageDraw, ImageFont
import os
import re
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

cv_router = Router()

def is_correct_text(text):
    contains_letters = re.search(r'[a-zA-Zа-яА-ЯіІїЇєЄґҐ]', text)
    only_symbols = re.fullmatch(r'[\W_]+', text)
    return bool(contains_letters) and not only_symbols

back2menu = "✏️ Повернутись до блоків"
backtomenu = "⚡️ Повернутись до блоків"

class CVStates(StatesGroup):
    position = State()
    languages = State()
    education = State()
    experience = State()
    skills = State()
    contacts = State()
    about = State()
    confirmation = State()

class TempCVStates(StatesGroup):
    position = State()
    languages = State()
    education = State()
    experience = State()
    skills = State()
    contacts = State()
    about = State()
    confirmation = State()

@cv_router.message(F.text == "📂 CV")
async def start_cv_menu(message: types.Message):
    await message.answer(
        "<b>Компанії шукають різних спеціалістів саме серед учасників Ярмарку!</b>\n\n"
        "Тож завантажуй своє резюме у форматі PDF або створи його тут за кілька хвилин!",
        parse_mode="HTML",
        reply_markup=get_cv_type_kb()
    )

@cv_router.message(F.text == "⚡️ Завантажити своє резюме")
async def ask_cv_file(message: types.Message):
    if not is_correct_text(message.text):
        await message.answer("⚠️ Схоже, що дані введені неправильно. Будь ласка, спробуй ще раз!")
        return
    await message.answer(
        "Завантаж своє CV у форматі PDF, і ми збережемо його для тебе!",
        reply_markup=main_menu_kb()
    )

@cv_router.message(F.document)
async def handle_cv_file(message: types.Message):
    if message.document.mime_type != "application/pdf":
        await message.answer("❗ Упс, схоже, що формат файлу неправильний. Спробуй ще раз, використовуючи PDF формат.")
        return

    max_file_size = 10 * 1024 * 1024  # 10 МБ
    if message.document.file_size > max_file_size:
        await message.answer("Упс🥲. Схоже, файл завеликий. Його розмір має бути не більшим за 10 МБ.")
        return

    try:
        file_id = message.document.file_id
        file = await message.bot.get_file(file_id)
        await message.bot.download_file(file.file_path, timeout=30)
    except Exception as e:
        await message.answer("🕒 Файл завантажується дуже довго… Перевір розмір і спробуй ще раз!")
        return

    await add_cv(
        user_id=message.from_user.id,
        cv_file_path=file_id,
        position='',
        languages='',
        education='',
        experience='',
        skills='',
        about='',
        contacts=''
    )
    await message.answer("✅ CV завантажено! 🎉", reply_markup=main_menu_kb())

@cv_router.message(F.text == "⚡️ Створити резюме разом")
async def cmd_start(message: types.Message, state: FSMContext):
    existing_cv = await get_cv(message.from_user.id)
    has_cv_data = existing_cv and all(existing_cv.get(field) for field in ['position', 'languages', 'education', 'experience', 'skills', 'about', 'contacts', 'cv_file_path'])
    if has_cv_data:
        await message.answer(
            "Бачимо, що ти вже створив резюме, то що чемпіоне, не зупиняєшся на одному?",
            reply_markup=has_cv_kb()
        )
        await state.set_state(CVStates.confirmation)
    else:
        await state.clear()
        await state.set_state(CVStates.position)
        await message.answer(
            "Тож почнімо, яка посада або напрям тебе цікавить? Наприклад: стажування в сфері Data Science, робота інженером-проєктувальником тощо. (Питання 1 з 7)",
            reply_markup=back2menu_kb()
        )

@cv_router.message(CVStates.position)
async def process_position(message: types.Message, state: FSMContext):
    if message.text in [back2menu, backtomenu]:
        await state.clear()
        await message.answer("Повертаємось до блоків!", reply_markup=main_menu_kb())
        return
    data = await state.get_data()
    if data.get("position"):
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Залишити попередню відповідь", callback_data="keep_previous_position")]
            ]
        )
        await message.answer(
            f"Тож почнімо, яка посада або напрям тебе цікавить?",
            reply_markup=keyboard
        )
        return

    if not is_correct_text(message.text):
        await message.answer("⚠️ Схоже, що дані введені неправильно. Спробуй ще раз!")
        return

    await state.update_data(position=message.text)
    await state.set_state(CVStates.languages)
    await message.answer("Якими мовами ти володієш. Вкажи рівень володіння. Наприклад: українська — рідна, англійська — B2. (Питання 2 з 7)")

@cv_router.callback_query(F.data == "keep_previous_position")
async def keep_previous_position(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(CVStates.languages)
    await callback.message.answer("Якими мовами ти володієш. Вкажи рівень володіння. Наприклад: українська — рідна, англійська — B2.")
    await callback.answer()

@cv_router.message(CVStates.languages)
async def process_languages(message: types.Message, state: FSMContext):
    if message.text in [back2menu, backtomenu]:
        await state.clear()
        await message.answer("Повертаємось до блоків!", reply_markup=main_menu_kb())
        return
    if not is_correct_text(message.text):
        await message.answer("⚠️ Схоже, що дані введені неправильно. Спробуй ще раз!")
        return

    VALID_LEVELS = {"A1", "A2", "B1", "B2", "C1", "C2", "А1", "А2", "В1", "В2", "С1", "С2"}
    text = message.text.lower()
    all_levels_raw = re.findall(r'\b([a-zA-Z][0-9])\b', message.text)
    all_levels_upper = [level.upper() for level in all_levels_raw]
    has_native = "рідна" in text
    valid_levels = [level for level in all_levels_upper if level in VALID_LEVELS]
    invalid_levels = [level for level in all_levels_upper if level not in VALID_LEVELS]

    if not has_native and not all_levels_raw:
        await message.answer("⚠️ Вкажи рівень володіння. Наприклад: українська — рідна, англійська — B2.")
        return
    if invalid_levels or (not has_native and not valid_levels):
        await message.answer("⚠️ Неправильний формат рівня. Спробуй ще раз!")
        return

    await state.update_data(languages=message.text)
    await state.set_state(CVStates.about)
    await message.answer("Розкажи коротко про себе. Чим цікавишся, яку сферу розглядаєш. (Питання 3 з 7)")

@cv_router.message(CVStates.about)
async def process_about(message: types.Message, state: FSMContext):
    if message.text in [back2menu, backtomenu]:
        await state.clear()
        await message.answer("Повертаємось до блоків!", reply_markup=main_menu_kb())
        return
    if not is_correct_text(message.text):
        await message.answer("⚠️ Схоже, що дані введені неправильно. Спробуй ще раз!")
        return
    await state.update_data(about=message.text)
    await state.set_state(CVStates.education)
    await message.answer("Вкажи університет та спеціальність. Якщо є курси, додай їх! (Питання 4 з 7)")

@cv_router.message(CVStates.education)
async def process_education(message: types.Message, state: FSMContext):
    if message.text in [back2menu, backtomenu]:
        await state.clear()
        await message.answer("Повертаємось до блоків!", reply_markup=main_menu_kb())
        return
    if not is_correct_text(message.text):
        await message.answer("⚠️ Схоже, що дані введені неправильно. Спробуй ще раз!")
        return
    await state.update_data(education=message.text)
    await state.set_state(CVStates.skills)
    await message.answer("Якими навичками ти володієш? Технічні, програми, особисті якості. (Питання 5 з 7)")

@cv_router.message(CVStates.skills)
async def process_skills(message: types.Message, state: FSMContext):
    if message.text in [back2menu, backtomenu]:
        await state.clear()
        await message.answer("Повертаємось до блоків!", reply_markup=main_menu_kb())
        return
    if not is_correct_text(message.text):
        await message.answer("⚠️ Схоже, що дані введені неправильно. Спробуй ще раз!")
        return
    await state.update_data(skills=message.text)
    await state.set_state(CVStates.experience)
    await message.answer("Маєш досвід роботи? Опиши посаду, обов'язки, період. Якщо ні — напиши «НІ». (Питання 6 з 7)")

@cv_router.message(CVStates.experience)
async def process_experience(message: types.Message, state: FSMContext):
    if message.text in [back2menu, backtomenu]:
        await state.clear()
        await message.answer("Повертаємось до блоків!", reply_markup=main_menu_kb())
        return
    if not is_correct_text(message.text):
        await message.answer("⚠️ Схоже, що дані введені неправильно. Спробуй ще раз!")
        return
    await state.update_data(experience=message.text)
    await state.set_state(CVStates.contacts)
    await message.answer("Залиш контакти: Email та номер телефону. (Питання 7 з 7)")

@cv_router.message(CVStates.contacts)
async def process_contacts(message: types.Message, state: FSMContext):
    if message.text in [back2menu, backtomenu]:
        await state.clear()
        await message.answer("Повертаємось до блоків!", reply_markup=main_menu_kb())
        return
    if not is_correct_text(message.text):
        await message.answer("⚠️ Схоже, що дані введені неправильно. Спробуй ще раз!")
        return
    await state.update_data(contacts=message.text)
    data = await state.get_data()

    user = await get_user(message.from_user.id)
    user_name = user.get("name", "") if user else ""

    summary = (
        f"Ім'я: {user_name}\n"
        f"Посада: {data['position']}\n"
        f"Мови: {data['languages']}\n"
        f"Освіта: {data['education']}\n"
        f"Досвід: {data['experience']}\n"
        f"Навички: {data['skills']}\n"
        f"Про кандидата: {data['about']}\n"
        f"Контакти: {data['contacts']}\n\n"
        "Все правильно?"
    )

    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Так"), KeyboardButton(text="Ні")]],
        resize_keyboard=True
    )
    await message.answer(summary, reply_markup=keyboard)
    await state.set_state(CVStates.confirmation)

def draw_wrapped_text(draw, text, font, fill, x, y, max_width_pixels, line_spacing=10):
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

@cv_router.message(CVStates.confirmation, F.text.casefold() == "так")
async def process_confirm_yes(message: types.Message, state: FSMContext):
    data = await state.get_data()
    try:
        user = await get_user(message.from_user.id)
        user_name = user.get("name", "") if user else ""
        name_parts = user_name.split()
        user_name_safe = "_".join(name_parts) if name_parts else f"user_{message.from_user.id}"
    except Exception as e:
        user_name = f"user_{message.from_user.id}"
        user_name_safe = user_name

    pdf_path = f"cv_{user_name_safe}.pdf"
    try:
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
            ("Бажана посада:", data['position']),
            ("Володіння мовами:", data['languages']),
            ("Освіта:", data['education']),
            ("Досвід:", data['experience']),
            ("Навички:", data['skills']),
            ("Про кандидата:", data['about']),
            ("Контакти:", data['contacts'])
        ]

        for label, content in fields:
            y_position = draw_wrapped_text(
                draw, label, font=font_text, fill="#111A94",
                x=x_position, y=y_position, max_width_pixels=max_width_pixels, line_spacing=10
            )
            y_position += 10
            y_position = draw_wrapped_text(
                draw, content, font=font_text, fill="#000000",
                x=x_position + 10, y=y_position, max_width_pixels=max_width_pixels - 10, line_spacing=10
            )
            y_position += 20

        image.save(pdf_path, "PDF")

        with open(pdf_path, "rb") as pdf_file:
            file_bytes = pdf_file.read()
            document = BufferedInputFile(file=file_bytes, filename=f"CV_{user_name_safe}.pdf")
            doc = await message.answer_document(document)
            file_id = doc.document.file_id

        await add_cv(
            user_id=message.from_user.id,
            cv_file_path=file_id,
            position=data['position'],
            languages=data['languages'],
            education=data['education'],
            experience=data['experience'],
            skills=data['skills'],
            about=data['about'],
            contacts=data['contacts']
        )
    except Exception as e:
        await message.answer("❗ Сталася помилка під час створення PDF. Спробуй ще раз пізніше.")
        return
    finally:
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

    await message.answer("Вітаємо! Твоє резюме готове. Тепер його побачать роботодавці.", reply_markup=main_menu_kb())
    await state.clear()

@cv_router.message(CVStates.confirmation, F.text.casefold() == "ні")
async def process_confirm_no(message: types.Message, state: FSMContext):
    if not is_correct_text(message.text):
        await message.answer("⚠️ Схоже, що дані введені неправильно. Спробуй ще раз!")
        return
    await state.clear()
    await state.set_state(CVStates.position)
    await message.answer("Гаразд, давай спробуємо ще раз. Яка посада або напрям тебе цікавить?", reply_markup=ReplyKeyboardRemove())

@cv_router.message(F.text == "⚡️ Повернутись до блоків")
async def back_to_menu(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Повертаємось до блоків!", reply_markup=main_menu_kb())

@cv_router.message(F.text == "✏️ Повернутись до блоків")
async def back_to_menu(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Повертаємось до блоків!", reply_markup=main_menu_kb())

@cv_router.message(F.text == "✏️ Редагувати попередній варіант")
async def change_existing_cv(message: types.Message, state: FSMContext):
    await message.answer("Гаразд, зараз на екрані ти бачиш всю інформацію з твого CV\nОбирай, яку з відповідей ти хочеш змінити, або заповнюй CV заново!")
    await state.clear()
    try:
        user = await get_user(message.from_user.id)
        user_name = user.get("name", "") if user else ""
    except Exception as e:
        user_name = ""
    cv_data = await get_cv(message.from_user.id)
    if cv_data:
        summary = (
            f"Ім'я: {user_name}\n"
            f"Посада: {cv_data['position']}\n"
            f"Мови: {cv_data['languages']}\n"
            f"Освіта: {cv_data['education']}\n"
            f"Досвід: {cv_data['experience']}\n"
            f"Навички: {cv_data['skills']}\n"
            f"Про кандидата: {cv_data['about']}\n"
            f"Контакти: {cv_data['contacts']}"
        )
        await message.answer(summary, reply_markup=change_cv_type_kb())
        await state.clear()

@cv_router.message(F.text == "✏️ Так, хочу додати ще одне CV")
async def change_existing_cv(message: types.Message, state: FSMContext):
    await message.answer("Чудово, давай почнемо створення нового CV!")
    await state.clear()
    await state.set_state(CVStates.position)
    await message.answer("Тож почнімо знову, яка посада або напрям тебе цікавить?", reply_markup=back2menu_kb())

async def update_cv_in_db(user_id: int, temp_data: dict):
    existing_cv = await get_cv(user_id)
    updated_cv = {
        "position": temp_data.get("position", existing_cv.get("position", "")),
        "languages": temp_data.get("languages", existing_cv.get("languages", "")),
        "education": temp_data.get("education", existing_cv.get("education", "")),
        "experience": temp_data.get("experience", existing_cv.get("experience", "")),
        "skills": temp_data.get("skills", existing_cv.get("skills", "")),
        "about": temp_data.get("about", existing_cv.get("about", "")),
        "contacts": temp_data.get("contacts", existing_cv.get("contacts", "")),
        "cv_file_path": existing_cv.get("cv_file_path", "")
    }
    await add_cv(
        user_id=user_id,
        position=updated_cv["position"],
        languages=updated_cv["languages"],
        education=updated_cv["education"],
        experience=updated_cv["experience"],
        skills=updated_cv["skills"],
        about=updated_cv["about"],
        contacts=updated_cv["contacts"],
        cv_file_path=updated_cv["cv_file_path"]
    )

@cv_router.callback_query(F.data.startswith("edit_"))
async def edit_field(callback: types.CallbackQuery, state: FSMContext):
    field_map = {
        "edit_position": ("position", "Яка посада або напрям тебе цікавить?"),
        "edit_languages": ("languages", "Якими мовами ти володієш? Вкажи рівень володіння."),
        "edit_education": ("education", "Вкажи університет та спеціальність, курси."),
        "edit_experience": ("experience", "Опиши досвід роботи або напиши «НІ»."),
        "edit_skills": ("skills", "Якими навичками ти володієш?"),
        "edit_about": ("about", "Розкажи коротко про себе."),
        "edit_contacts": ("contacts", "Залиш свої контактні дані!")
    }

    callback_data = callback.data
    field, question = field_map.get(callback_data, (None, None))

    if not field:
        await callback.answer("Невідома дія!", show_alert=True)
        return

    await state.set_state(getattr(TempCVStates, field))
    await callback.message.answer(question)
    await callback.answer()

@cv_router.message(TempCVStates.position)
async def edit_position(message: types.Message, state: FSMContext):
    if not is_correct_text(message.text):
        await message.answer("⚠️ Схоже, що дані введені неправильно. Спробуй ще раз!")
        return
    await state.update_data(position=message.text)
    temp_data = await state.get_data()
    await update_cv_in_db(message.from_user.id, temp_data)
    await message.answer("Зміни збережено!\nОбери наступне поле.", reply_markup=change_cv_type_kb())
    await state.clear()

@cv_router.message(TempCVStates.languages)
async def edit_languages(message: types.Message, state: FSMContext):
    if not is_correct_text(message.text):
        await message.answer("⚠️ Схоже, що дані введені неправильно. Спробуй ще раз!")
        return
    await state.update_data(languages=message.text)
    temp_data = await state.get_data()
    await update_cv_in_db(message.from_user.id, temp_data)
    await message.answer("Зміни збережено!\nОбери наступне поле.", reply_markup=change_cv_type_kb())
    await state.clear()

@cv_router.message(TempCVStates.education)
async def edit_education(message: types.Message, state: FSMContext):
    if not is_correct_text(message.text):
        await message.answer("⚠️ Схоже, що дані введені неправильно. Спробуй ще раз!")
        return
    await state.update_data(education=message.text)
    temp_data = await state.get_data()
    await update_cv_in_db(message.from_user.id, temp_data)
    await message.answer("Зміни збережено!\nОбери наступне поле.", reply_markup=change_cv_type_kb())
    await state.clear()

@cv_router.message(TempCVStates.experience)
async def edit_experience(message: types.Message, state: FSMContext):
    if not is_correct_text(message.text):
        await message.answer("⚠️ Схоже, що дані введені неправильно. Спробуй ще раз!")
        return
    await state.update_data(experience=message.text)
    temp_data = await state.get_data()
    await update_cv_in_db(message.from_user.id, temp_data)
    await message.answer("Зміни збережено!\nОбери наступне поле.", reply_markup=change_cv_type_kb())
    await state.clear()

@cv_router.message(TempCVStates.skills)
async def edit_skills(message: types.Message, state: FSMContext):
    if not is_correct_text(message.text):
        await message.answer("⚠️ Схоже, що дані введені неправильно. Спробуй ще раз!")
        return
    await state.update_data(skills=message.text)
    temp_data = await state.get_data()
    await update_cv_in_db(message.from_user.id, temp_data)
    await message.answer("Зміни збережено!\nОбери наступне поле.", reply_markup=change_cv_type_kb())
    await state.clear()

@cv_router.message(TempCVStates.about)
async def edit_about(message: types.Message, state: FSMContext):
    if not is_correct_text(message.text):
        await message.answer("⚠️ Схоже, що дані введені неправильно. Спробуй ще раз!")
        return
    await state.update_data(about=message.text)
    temp_data = await state.get_data()
    await update_cv_in_db(message.from_user.id, temp_data)
    await message.answer("Зміни збережено!\nОбери наступне поле.", reply_markup=change_cv_type_kb())
    await state.clear()

@cv_router.message(TempCVStates.contacts)
async def edit_contacts(message: types.Message, state: FSMContext):
    if not is_correct_text(message.text):
        await message.answer("⚠️ Схоже, що дані введені неправильно. Спробуй ще раз!")
        return
    await state.update_data(contacts=message.text)
    temp_data = await state.get_data()
    await update_cv_in_db(message.from_user.id, temp_data)
    await message.answer("Зміни збережено!\nОбери наступне поле.", reply_markup=change_cv_type_kb())
    await state.clear()

@cv_router.callback_query(F.data == "confirm_editing")
async def confirm_editing(callback: types.CallbackQuery, state: FSMContext):
    temp_data = await state.get_data()
    existing_cv = await get_cv(callback.from_user.id)

    updated_cv = {
        "position": temp_data.get("position", existing_cv.get("position", "")),
        "languages": temp_data.get("languages", existing_cv.get("languages", "")),
        "education": temp_data.get("education", existing_cv.get("education", "")),
        "experience": temp_data.get("experience", existing_cv.get("experience", "")),
        "skills": temp_data.get("skills", existing_cv.get("skills", "")),
        "about": temp_data.get("about", existing_cv.get("about", "")),
        "contacts": temp_data.get("contacts", existing_cv.get("contacts", ""))
    }
    try:
        user = await get_user(callback.from_user.id)
        user_name = user.get("name", "") if user else ""
        name_parts = user_name.split()
        user_name_safe = "_".join(name_parts) if name_parts else f"user_{callback.from_user.id}"
    except Exception as e:
        user_name = f"user_{callback.from_user.id}"
        user_name_safe = user_name
    pdf_path = f"cv_{user_name_safe}.pdf"

    try:
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
            ("Бажана посада:", updated_cv['position']),
            ("Володіння мовами:", updated_cv['languages']),
            ("Освіта:", updated_cv['education']),
            ("Досвід:", updated_cv['experience']),
            ("Навички:", updated_cv['skills']),
            ("Про кандидата:", updated_cv['about']),
            ("Контакти:", updated_cv['contacts'])
        ]

        for label, content in fields:
            y_position = draw_wrapped_text(
                draw, label, font=font_text, fill="#111A94",
                x=x_position, y=y_position, max_width_pixels=max_width_pixels, line_spacing=10
            )
            y_position += 10
            y_position = draw_wrapped_text(
                draw, content, font=font_text, fill="#000000",
                x=x_position + 10, y=y_position, max_width_pixels=max_width_pixels - 10, line_spacing=10
            )
            y_position += 20

        image.save(pdf_path, "PDF")

        with open(pdf_path, "rb") as pdf_file:
            file_bytes = pdf_file.read()
            document = BufferedInputFile(file=file_bytes, filename=f"CV_{user_name_safe}.pdf")
            doc = await callback.message.answer_document(document)
            file_id = doc.document.file_id

        await add_cv(
            user_id=callback.from_user.id,
            position=updated_cv["position"],
            languages=updated_cv["languages"],
            education=updated_cv["education"],
            experience=updated_cv["experience"],
            skills=updated_cv["skills"],
            about=updated_cv["about"],
            contacts=updated_cv["contacts"],
            cv_file_path=file_id
        )
    except Exception as e:
        await callback.message.answer("❗ Сталася помилка під час створення PDF. Спробуй ще раз пізніше.")
        return
    finally:
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

    await callback.message.answer("Зміни збережено! Твоє резюме оновлено та надіслано в чат.", reply_markup=main_menu_kb())
    await state.clear()