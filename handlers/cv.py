from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InputFile
from aiogram.fsm.state import State, StatesGroup
from utils.database import get_user, add_cv
from keyboards.cv_kb import get_cv_type_kb
from keyboards.main_menu_kb import main_menu_kb
from PIL import Image, ImageDraw, ImageFont
import os
import re
import textwrap
from aiogram.types import BufferedInputFile

cv_router = Router()


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


@cv_router.message(F.text == "Завантажити своє резюме") # кнопка з клавіатури сівішок
async def ask_cv_file(message: types.Message):
    await message.answer(
        "Завантаж своє CV у форматі PDF, і ми збережемо його для тебе!",
        reply_markup=ReplyKeyboardRemove()
    )


@cv_router.message(F.document)
async def handle_cv_file(message: types.Message):
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


@cv_router.message(F.text == "Створити резюме разом") # кнопка з клавіатури сівішок
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    await state.set_state(CVStates.position)
    await message.answer("Тож почнімо, яка посада або напрям тебе цікавить? Наприклад: стажування в сфері Data Science, робота інженером-проєктувальником тощо.", reply_markup=ReplyKeyboardRemove())


@cv_router.message(CVStates.position) # питання студіків
async def process_position(message: types.Message, state: FSMContext):
    await state.update_data(position=message.text)
    await state.set_state(CVStates.languages)
    await message.answer("Якими мовами ти володієш. Вкажи рівень володіння для кожної мови. Наприклад: українська — рідна, англійська — B2.")


@cv_router.message(CVStates.languages)
async def process_languages(message: types.Message, state: FSMContext):

    VALID_LEVELS = {"A1", "A2", "B1", "B2", "C1", "C2"}
    text = message.text.lower()
    levels_found = re.findall(r'\b([a-cA-C][1-2])\b', message.text)
    levels_found_upper = [level.upper() for level in levels_found]

    has_native = "рідна" in text
    has_valid_level = any(level in VALID_LEVELS for level in levels_found_upper)
    invalid_levels = [level for level in levels_found_upper if level not in VALID_LEVELS]

    if not has_native and not levels_found:
        await message.answer(
            "⚠️ Схоже, що ти не вказав(-ла) рівень володіння мовами.\n"
            "Будь ласка, використовуй або слово «рідна», або рівні A1, A2, B1, B2, C1, C2.\n"
            "Наприклад:\n"
            "— українська — рідна\n"
            "— англійська — B2"
        )
        return

    if invalid_levels:
        await message.answer(
            f"⚠️ Виявлено неправильні рівні: {', '.join(invalid_levels)}.\n"
            f"Будь ласка, використовуй лише ці рівні: A1, A2, B1, B2, C1, C2 або слово «рідна».\n"
            "Наприклад:\n"
            "— українська — рідна\n"
            "— англійська — B2"
        )
        return

    if not has_native and not has_valid_level:
        # Якщо нема слова "рідна" і нема жодного правильного рівня
        await message.answer(
            "⚠️ Ти вказав(-ла) рівень, але він некоректний.\n"
            "Будь ласка, використовуй лише ці рівні: A1, A2, B1, B2, C1, C2 або слово «рідна».\n"
            "Наприклад:\n"
            "— українська — рідна\n"
            "— англійська — B2"
        )
        return

    # Якщо все добре
    await state.update_data(languages=message.text)
    await state.set_state(CVStates.about)
    await message.answer(
        "Розкажи коротко про себе. Чим цікавишся, яку сферу розглядаєш, чому хочеш працювати в обраному напрямку."
    )



@cv_router.message(CVStates.about)
async def process_languages(message: types.Message, state: FSMContext):
    await state.update_data(about=message.text)
    await state.set_state(CVStates.education)
    await message.answer("Не забуваймо і про освіту! Вкажи університет та спеціальність на якій навчаєшся. Якщо можеш похвалитись пройденими курсами, тоді обовʼязково це зроби!")


@cv_router.message(CVStates.education)
async def process_experience(message: types.Message, state: FSMContext):
    await state.update_data(education=message.text)
    await state.set_state(CVStates.skills)
    await message.answer("Якими навичками ти володієш. Технічні навички, інструменти, програми, а також особисті якості, які тобі допомагають у роботі.")


@cv_router.message(CVStates.skills)
async def process_education(message: types.Message, state: FSMContext):
    await state.update_data(skills=message.text)
    await state.set_state(CVStates.experience)
    await message.answer("Маєш досвід роботи або практики? Якщо так, коротко опиши посаду, обов'язки та період. Якщо досвіду немає — просто напиши «НІ».")



@cv_router.message(CVStates.experience)
async def process_skills(message: types.Message, state: FSMContext):
    await state.update_data(experience=message.text)
    await state.set_state(CVStates.contacts)
    await message.answer("І останнє залиш свої контактні дані! Email та номер телефону, щоб роботодавці могли з тобою зв'язатися.")


@cv_router.message(CVStates.contacts)
async def process_contacts(message: types.Message, state: FSMContext):
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

    pdf_path = f"cv_{message.from_user.id}.pdf"
    image.save(pdf_path, "PDF")

    with open(pdf_path, "rb") as pdf_file:
        file_bytes = pdf_file.read()
        document = BufferedInputFile(file=file_bytes, filename=f"CV_{message.from_user.id}.pdf")
        doc = await message.answer_document(document)
        file_id = doc.document.file_id


    await add_cv(message.from_user.id, cv_file_path=file_id) 

    os.remove(pdf_path)

    await message.answer("Вітаємо! Твоє резюме готове. Тепер його побачать роботодавці.", reply_markup=main_menu_kb())
    await state.clear()

@cv_router.message(CVStates.confirmation, F.text.casefold() == "ні")
async def process_confirm_no(message: types.Message, state: FSMContext):
    await state.clear()
    await state.set_state(CVStates.position)
    await message.answer("Гаразд, давай спробуємо ще раз. Яка посада або напрям тебе цікавить? Наприклад: стажування в сфері Data Science, робота інженером-проєктувальником тощо.", reply_markup=ReplyKeyboardRemove())


@cv_router.message(F.text == "Повернутись до блоків") # кнопка з клавіатури сівішок
async def back_to_menu(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Повертаємось до блоків!", reply_markup=main_menu_kb())
