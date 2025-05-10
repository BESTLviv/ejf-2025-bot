from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InputFile
from aiogram.fsm.state import State, StatesGroup
from utils.database import get_user, add_cv
from keyboards.cv_kb import get_cv_type_kb, change_cv_type_kb, has_cv_kb
from keyboards.main_menu_kb import main_menu_kb
from PIL import Image, ImageDraw, ImageFont
import os
import re
import textwrap
from aiogram.types import BufferedInputFile
from utils.database import get_cv



cv_router = Router()

def is_correct_text(text):
    contains_letters = re.search(r'[a-zA-Zа-яА-ЯіІїЇєЄґҐ]', text)
    only_symbols = re.fullmatch(r'[\W_]+', text) 
    return bool(contains_letters) and not only_symbols


class CVStates(StatesGroup):# клас для збору даних при заповненні cv 
    position = State()
    languages = State()
    education = State()
    experience = State()
    skills = State()
    contacts = State()
    about = State()
    confirmation = State()


@cv_router.message(F.text == "📂 CV") # кнопка з головної клавіатури
async def start_cv_menu(message: types.Message):
             
        await message.answer(
        "Компанії шукають різних спеціалістів саме серед учасників Ярмарку!\n"
        "Тож завантажуй своє резюме у форматі PDF або створи його тут за кілька хвилин!",
        reply_markup=get_cv_type_kb()
    )


@cv_router.message(F.text == "⚡️ Завантажити своє резюме") # кнопка з клавіатури сівішок
async def ask_cv_file(message: types.Message):
    if not is_correct_text(message.text):
        await message.answer(
            "⚠️ Схоже, що дані введені неправильно. Будь ласка, спробуй ще раз!"
        )
        return
    await message.answer(
        "Завантаж своє CV у форматі PDF, і ми збережемо його для тебе!",
        reply_markup=main_menu_kb()
    )


@cv_router.message(F.document)
async def handle_cv_file(message: types.Message):
    if not is_correct_text(message.text):
        await message.answer(
            "⚠️ Схоже, що дані введені неправильно. Будь ласка, спробуй ще раз!"
        )
        return
    if message.document.mime_type != "application/pdf":
        await message.answer("❗ Упс, схоже, що формат файлу неправильний. Спробуй ще раз,використовуючи pdf формат.")
        return

    max_file_size = 10 * 1024 * 1024  # 10 МБ 
    if message.document.file_size > max_file_size:
        await message.answer("Упс🥲. Схоже, файл завеликий для завантаження. Його розмір має бути не більшим 10 МБ. Спробуй зменшити вагу файлу й надіслати ще раз!")
        return

    try:
        file_id = message.document.file_id
        file = await message.bot.get_file(file_id)
        await message.bot.download_file(file.file_path, timeout=30)  # Обмеження часу завантаження в 30 секунд
    except Exception as e:
        await message.answer("🕒 Файл завантажується дуже довго… Можливо, він перевищує дозволений розмір у 10 МБ. Перевір, будь ласка, і спробуй ще раз!")
        return

    await add_cv(message.from_user.id, cv_file_path=file_id)
    await message.answer("✅ CV завантажено! 🎉", reply_markup=main_menu_kb())


@cv_router.message(F.text == "⚡️ Створити резюме разом")  # кнопка з клавіатури
async def cmd_start(message: types.Message, state: FSMContext):
    existing_cv = await get_cv(message.from_user.id)
    has_cv_data = existing_cv and all(existing_cv.get(field) for field in ['position', 'languages', 'education', 'experience', 'skills', 'about', 'contacts'])
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
            "Тож почнімо, яка посада або напрям тебе цікавить? Наприклад: стажування в сфері Data Science, робота інженером-проєктувальником тощо.",
            reply_markup=ReplyKeyboardRemove()
        )


@cv_router.message(CVStates.position) # питання студіків
async def process_position(message: types.Message, state: FSMContext):
    if not is_correct_text(message.text):
        await message.answer(
            "⚠️ Схоже, що дані введені неправильно. Будь ласка, спробуй ще раз!"
        )
        return
    await state.update_data(position=message.text)
    await state.set_state(CVStates.languages)
    await message.answer("Якими мовами ти володієш. Вкажи рівень володіння для кожної мови. Наприклад: українська — рідна, англійська — B2.")

@cv_router.message(CVStates.languages)
async def process_languages(message: types.Message, state: FSMContext):
    if not is_correct_text(message.text):
        await message.answer(
            "⚠️ Схоже, що дані введені неправильно. Будь ласка, спробуй ще раз!"
        )
        return

    VALID_LEVELS = {"A1", "A2", "B1", "B2", "C1", "C2","А1", "А2", "В1", "В2", "С1", "С2"}
    text = message.text.lower()
    all_levels_raw = re.findall(r'\b([a-zA-Z][0-9])\b', message.text)
    all_levels_upper = [level.upper() for level in all_levels_raw]

    has_native = "рідна" in text
    valid_levels = [level for level in all_levels_upper if level in VALID_LEVELS]
    invalid_levels = [level for level in all_levels_upper if level not in VALID_LEVELS]

    if not has_native and not all_levels_raw:
        await message.answer(
            "⚠️ Схоже, що дані введені неправильно. Будь ласка, спробуй ще раз!\n" 
            "Вкажи рівень володіння для кожної мови. Наприклад: українська — рідна, англійська — B2."
        )
        return

    if invalid_levels:
        await message.answer(
            "⚠️ Схоже, що дані введені неправильно. Будь ласка, спробуй ще раз!\n" 
            "Вкажи рівень володіння для кожної мови. Наприклад: українська — рідна, англійська — B2."
        )
        return

    if not has_native and not valid_levels:
        await message.answer(
            "⚠️ Схоже, що дані введені неправильно. Будь ласка, спробуй ще раз!\n" 
            "Вкажи рівень володіння для кожної мови. Наприклад: українська — рідна, англійська — B2."
        )
        return

    await state.update_data(languages=message.text)
    await state.set_state(CVStates.about)
    await message.answer(
        "Розкажи коротко про себе. Чим цікавишся, яку сферу розглядаєш, чому хочеш працювати в обраному напрямку."
    )




@cv_router.message(CVStates.about)
async def process_languages(message: types.Message, state: FSMContext):
    if not is_correct_text(message.text):
        await message.answer(
            "⚠️ Схоже, що дані введені неправильно. Будь ласка, спробуй ще раз!"
        )
        return
    await state.update_data(about=message.text)
    await state.set_state(CVStates.education)
    await message.answer("Не забуваймо і про освіту! Вкажи університет та спеціальність на якій навчаєшся. Якщо можеш похвалитись пройденими курсами, тоді обовʼязково це зроби!")


@cv_router.message(CVStates.education)
async def process_experience(message: types.Message, state: FSMContext):
    if not is_correct_text(message.text):
        await message.answer(
            "⚠️ Схоже, що дані введені неправильно. Будь ласка, спробуй ще раз!"
        )
        return
    await state.update_data(education=message.text)
    await state.set_state(CVStates.skills)
    await message.answer("Якими навичками ти володієш. Технічні навички, інструменти, програми, а також особисті якості, які тобі допомагають у роботі.")


@cv_router.message(CVStates.skills)
async def process_education(message: types.Message, state: FSMContext):
    if not is_correct_text(message.text):
        await message.answer(
            "⚠️ Схоже, що дані введені неправильно. Будь ласка, спробуй ще раз!"
        )
        return
    await state.update_data(skills=message.text)
    await state.set_state(CVStates.experience)
    await message.answer("Маєш досвід роботи або практики? Якщо так, коротко опиши посаду, обов'язки та період. Якщо досвіду немає — просто напиши «НІ».")



@cv_router.message(CVStates.experience)
async def process_skills(message: types.Message, state: FSMContext):
    if not is_correct_text(message.text):
        await message.answer(
            "⚠️ Схоже, що дані введені неправильно. Будь ласка, спробуй ще раз!"
        )
        return
    await state.update_data(experience=message.text)
    await state.set_state(CVStates.contacts)
    await message.answer("І останнє залиш свої контактні дані! Email та номер телефону, щоб роботодавці могли з тобою зв'язатися.")


@cv_router.message(CVStates.contacts)
async def process_contacts(message: types.Message, state: FSMContext):
    if not is_correct_text(message.text):
        await message.answer(
            "⚠️ Схоже, що дані введені неправильно. Будь ласка, спробуй ще раз!"
        )
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
        f"Контакти: {data['contacts']}\n\n"
        "Все правильно?"
    )

    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Так"), KeyboardButton(text="Ні")]],
        resize_keyboard=True
    )
    await message.answer(summary, reply_markup=keyboard)
    await state.set_state(CVStates.confirmation)

from utils.database import get_user, add_cv

@cv_router.message(CVStates.confirmation, F.text.casefold() == "так")
async def process_confirm_yes(message: types.Message, state: FSMContext):
    data = await state.get_data()
    try:
        user = await get_user(message.from_user.id)
        user_name = user.get("name", "") if user else ""
    except Exception as e:
        user_name = ""

    image = Image.open("templates/cv_template.png").convert("RGB")
    draw = ImageDraw.Draw(image)
    font_text = ImageFont.truetype("fonts/Nunito-Regular.ttf", 14)
    font_title = ImageFont.truetype("fonts/Exo2-Regular.ttf", 36)

    def draw_wrapped_text(draw, text, font, fill, x, y, max_width):
        lines = textwrap.wrap(text, width=max_width)
        line_height = font.getbbox("A")[1] 
        for line in lines:
            draw.text((x, y), line, font=font, fill=fill)
            y += line_height 

    draw_wrapped_text(draw, f"{user_name}", font=font_title, fill="#111A94", x=300, y=70, max_width=40)
    draw_wrapped_text(draw, f"Бажана посада:\n {data['position']}", font=font_text, fill="#111A94", x=300, y=220, max_width=100)
    draw_wrapped_text(draw, f"Володіння мовами:\n{data['languages']}", font=font_text, fill="#111A94", x=300, y=320, max_width=100)
    draw_wrapped_text(draw, f"Освіта:\n{data['education']}", font=font_text, fill="#111A94", x=300, y=420, max_width=100)
    draw_wrapped_text(draw, f"Досвід:\n{data['experience']}", font=font_text, fill="#111A94", x=300, y=520, max_width=100)
    draw_wrapped_text(draw, f"Навички:\n{data['skills']}", font=font_text, fill="#111A94", x=300, y=620, max_width=100)
    draw_wrapped_text(draw, f"Про кандидата:\n{data['about']}", font=font_text, fill="#111A94", x=300, y=720, max_width=100)
    draw_wrapped_text(draw, f"Контакти:\n{data['contacts']}", font=font_text, fill="#111A94", x=300, y=820, max_width=100)
    try:
        user = await get_user(message.from_user.id)
        full_name = user.get("name", "") if user else ""
        name_parts = full_name.split()
        user_name = "_".join(name_parts) if len(name_parts) > 0 else ""
    except Exception as e:
        user_name = ""
    pdf_path = f"cv{user_name}.pdf"
    image.save(pdf_path, "PDF")

    with open(pdf_path, "rb") as pdf_file:
        file_bytes = pdf_file.read()
        document = BufferedInputFile(file=file_bytes, filename=f"CV{user_name}.pdf")
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
    os.remove(pdf_path)

    await message.answer("Вітаємо! Твоє резюме готове. Тепер його побачать роботодавці.", reply_markup=main_menu_kb())
    await state.clear()

@cv_router.message(CVStates.confirmation, F.text.casefold() == "ні")
async def process_confirm_no(message: types.Message, state: FSMContext):
    if not is_correct_text(message.text):
        await message.answer(
            "⚠️ Схоже, що дані введені неправильно. Будь ласка, спробуй ще раз!"
        )
        return
    await state.clear()
    await state.set_state(CVStates.position)
    await message.answer("Гаразд, давай спробуємо ще раз. Яка посада або напрям тебе цікавить? Наприклад: стажування в сфері Data Science, робота інженером-проєктувальником тощо.", reply_markup=ReplyKeyboardRemove())


@cv_router.message(F.text == "⚡️ Повернутись до блоків" ) # кнопка з клавіатури сівішок
async def back_to_menu(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Повертаємось до блоків!", reply_markup=main_menu_kb())

#==================================================================================================================================

@cv_router.message(F.text == "✏️ Повернутись до блоків" ) # кнопка з клавіатури якщо сівішка вже є
async def back_to_menu(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Повертаємось до блоків!", reply_markup=main_menu_kb())


@cv_router.message(F.text == "✏️ Редагувати попередній варіант") # кнопка з клавіатури якщо сівішка вже є
async def change_existing_cv(message: types.Message, state: FSMContext):
    await message.answer("Гаразд, зараз на екрані ти бачиш всю інфрмацію зі створеного CV\n\n Обирай яку з відповідей ти хочеш змінити або заповнюй CV заново!")
    await state.clear()
    try:
        user = await get_user(message.from_user.id)
        user_name = user.get("name", "") if user else ""
    except Exception as e:
        user_name = ""
    cv_data = await get_cv(message.from_user.id)
    if cv_data:
        summary = (
            f"Ім'я:{user_name}\n"
            f"Посада: {cv_data['position']}\n"
            f"Мови: {cv_data['languages']}\n"
            f"Освіта: {cv_data['education']}\n"
            f"Досвід: {cv_data['experience']}\n"
            f"Навички: {cv_data['skills']}\n"
            f"Про кандидата: {cv_data['about']}\n"
            f"Контакти: {cv_data['contacts']}"
        )
        await message.answer(summary, reply_markup=change_cv_type_kb())
    await state.set_state(CVStates.position)
    await message.answer("Тож почнімо, яка посада або напрям тебе цікавить? Наприклад: стажування в сфері Data Science, робота інженером-проєктувальником тощо.", reply_markup=ReplyKeyboardRemove())
    