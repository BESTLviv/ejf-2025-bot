from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InputFile
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import CommandStart
from utils.database import get_user, add_cv
from keyboards.cv_kb import get_cv_type_kb
from keyboards.main_menu_kb import main_menu_kb
from PIL import Image, ImageDraw, ImageFont
import os
from aiogram.types import BufferedInputFile

cv_router = Router()


class CVStates(StatesGroup):
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
        "Компанії шукають різних спеціалістів саме серед учасників Ярмарку!\n"
        "Тож завантажуй своє резюме у форматі PDF або створи його тут за кілька хвилин!",
        reply_markup=get_cv_type_kb()
    )


@cv_router.message(F.text == "📂 Завантажити CV")
async def ask_cv_file(message: types.Message):
    await message.answer(
        "Завантаж своє CV у форматі PDF, і ми збережемо його для тебе!",
        reply_markup=ReplyKeyboardRemove()
    )


@cv_router.message(F.document)
async def handle_cv_file(message: types.Message):
    if message.document.mime_type != "application/pdf":
        await message.answer("❗ Це не PDF. Спробуй ще раз.")
        return

    file_id = message.document.file_id
    await add_cv(message.from_user.id, cv_file_path=file_id)
    await message.answer("✅ CV завантажено! 🎉", reply_markup=main_menu_kb())


@cv_router.message(F.text == "📝 Створити CV")
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    await state.set_state(CVStates.position)
    await message.answer("Яка посада вас цікавить?", reply_markup=ReplyKeyboardRemove())


@cv_router.message(CVStates.position)
async def process_position(message: types.Message, state: FSMContext):
    await state.update_data(position=message.text)
    await state.set_state(CVStates.languages)
    await message.answer("Які мови ви знаєте?")


@cv_router.message(CVStates.languages)
async def process_languages(message: types.Message, state: FSMContext):
    await state.update_data(languages=message.text)
    await state.set_state(CVStates.about)
    await message.answer("Пару слів про вас")

@cv_router.message(CVStates.about)
async def process_languages(message: types.Message, state: FSMContext):
    await state.update_data(about=message.text)
    await state.set_state(CVStates.education)
    await message.answer("Ваша освіта?")


@cv_router.message(CVStates.education)
async def process_education(message: types.Message, state: FSMContext):
    await state.update_data(education=message.text)
    await state.set_state(CVStates.experience)
    await message.answer("Ваш досвід роботи?")


@cv_router.message(CVStates.experience)
async def process_experience(message: types.Message, state: FSMContext):
    await state.update_data(experience=message.text)
    await state.set_state(CVStates.skills)
    await message.answer("Ваші навички?")


@cv_router.message(CVStates.skills)
async def process_skills(message: types.Message, state: FSMContext):
    await state.update_data(skills=message.text)
    await state.set_state(CVStates.contacts)
    await message.answer("Контактна інформація?")


@cv_router.message(CVStates.contacts)
async def process_contacts(message: types.Message, state: FSMContext):
    await state.update_data(contacts=message.text)
    data = await state.get_data()

    user = await get_user(message.from_user.id)
    user_name = user.get("name", "") if user else "Невідомо"

    summary = (
        f"Ім'я: {user_name}\n"
        f"Посада: {data['position']}\n"
        f"Мови: {data['languages']}\n"
        f"Освіта: {data['education']}\n"
        f"Досвід: {data['experience']}\n"
        f"Навички: {data['skills']}\n"
        f"Контакти: {data['contacts']}\n\n"
        "Все вірно?"
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
        print(f"Error getting user: {e}")
        user_name = ""
    template_path = "templates/cv_template.png"
    if not os.path.exists(template_path):
        await message.answer("⚠️ Шаблон CV не знайдено. Перевірте, чи файл 'cv_template.png' існує в папці 'templates'.")
        return

    image = Image.open("templates/cv_template.png").convert("RGB")
    draw = ImageDraw.Draw(image)
    font_text = ImageFont.truetype("fonts/Nunito-Regular.ttf", 18)
    font_title = ImageFont.truetype("fonts/Exo2-Regular.ttf", 36)

    draw.text((150, 70),  f"Ім'я: {user_name}", font=font_title, fill="#111A94")
    draw.text((150, 120), f"Очікувана посада: {data['position']}", font=font_text, fill="#111A94")
    draw.text((150, 160), f"Володіння мовами: {data['languages']}", font=font_text, fill="#111A94")
    draw.text((150, 200), f"Освіта: {data['education']}", font=font_text, fill="#111A94")
    draw.text((150, 240), f"Досвід: {data['experience']}", font=font_text, fill="#111A94")
    draw.text((150, 270), f"Навички: {data['skills']}", font=font_text, fill="#111A94")
    draw.text((150, 300), f"Про кандидата: {data['about']}", font=font_text, fill="#111A94")
    draw.text((150, 320), f"Контакти: {data['contacts']}", font=font_text, fill="#111A94")

    pdf_path = f"cv_{message.from_user.id}.pdf"
    image.save(pdf_path, "PDF")

    with open(pdf_path, "rb") as pdf_file:
        file_bytes = pdf_file.read()
        document = BufferedInputFile(file=file_bytes, filename=f"CV_{message.from_user.id}.pdf")
        doc = await message.answer_document(document)
        file_id = doc.document.file_id


    await add_cv(message.from_user.id, file_id)

    os.remove(pdf_path)

    await message.answer("✅ CV згенеровано!", reply_markup=main_menu_kb())
    await state.clear()

@cv_router.message(CVStates.confirmation, F.text.casefold() == "ні")
async def process_confirm_no(message: types.Message, state: FSMContext):
    await state.clear()
    await state.set_state(CVStates.position)
    await message.answer("Добре, давай спробуємо ще раз. Яка посада вас цікавить?", reply_markup=ReplyKeyboardRemove())


@cv_router.message(F.text == "⬅️ Назад")
async def back_to_menu(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Повертаємось до головного меню!", reply_markup=main_menu_kb())
