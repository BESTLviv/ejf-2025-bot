from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from utils.database import add_cv
from keyboards.cv_kb import get_cv_type_kb
from states.cv import CVForm
from keyboards.main_menu_kb import main_menu_kb
from fpdf import FPDF
import os
from aiogram.types import FSInputFile
import os
import requests
from fpdf import FPDF
from aiogram.types import FSInputFile


router = Router()

@router.message(F.text == "📂 CV")
async def start_cv_menu(message: types.Message):
    await message.answer(
        "Компанії шукають різних спеціалістів саме серед учасників Ярмарку!\n"
        "Тож завантажуй своє резюме у форматі PDF та чекай дзвіночка!\n\n"
        "Не маєш CV? Я допоможу – відповідай на декілька запитань, і за кілька хвилин матимеш готове резюме!",
        reply_markup=get_cv_type_kb()  
    )

@router.message(F.text == "📂 Завантажити CV")
async def ask_cv_file(message: types.Message):
    await message.answer(
        "Завантаж своє CV у форматі PDF, і ми збережемо його для тебе!",
        reply_markup=ReplyKeyboardRemove()  
    )

@router.message(F.document)
async def handle_cv_file(message: types.Message):
    if message.document.mime_type != "application/pdf":
        await message.answer("❗Упс, схоже, що формат файлу неправильний. Спробуй ще раз, використовуючи PDF")
        return

    file_id = message.document.file_id
    await add_cv(message.from_user.id, cv_file_path=file_id)
    await message.answer("✅ CV завантажено! Ти красень! 🎉",
    reply_markup=main_menu_kb())


@router.message(F.text == "⬅️ Назад")
async def back_to_menu(message: types.Message):
    await message.answer(
        "Повертаємось до головного меню!",
        reply_markup=main_menu_kb()
    )



FONT_URL = "https://github.com/dejavu-fonts/dejavu-fonts/raw/version_2_37/ttf/DejaVuSans.ttf"
FONT_DIR = "fonts"
FONT_PATH = os.path.join(FONT_DIR, "DejaVuSans.ttf")

# Функція для завантаження шрифту
def download_font():
    if not os.path.exists(FONT_PATH):
        os.makedirs(FONT_DIR, exist_ok=True)
        with open(FONT_PATH, "wb") as f:
            f.write(requests.get(FONT_URL).content)

async def generate_and_send_cv(callback_query, user_data):
    download_font()  # Завантажує шрифт, якщо його немає

    filename = f"{user_data['full_name'].replace(' ', '_')}_cv"
    pdf_path = f"{filename}.pdf"

    pdf = FPDF()
    pdf.add_page()
    pdf.add_font("DejaVu", "", FONT_PATH, uni=True)
    pdf.set_font("DejaVu", size=12)

    pdf.cell(200, 10, txt="Curriculum Vitae", ln=True, align='C')
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Ім'я та прізвище: {user_data['full_name']}", ln=True)
    pdf.cell(200, 10, txt=f"Роки навчання: {user_data.get('education_years', '')}", ln=True)
    pdf.cell(200, 10, txt=f"Університет: {user_data.get('education', '')}", ln=True)
    pdf.cell(200, 10, txt=f"Спеціальність: {user_data.get('speciality', '')}", ln=True)
    pdf.ln(5)

    if user_data.get("skills"):
        pdf.multi_cell(0, 10, txt=f"Навички: {user_data['skills']}")
    if user_data.get("experience"):
        pdf.multi_cell(0, 10, txt=f"Досвід: {user_data['experience']}")
    if user_data.get("qualities"):
        pdf.multi_cell(0, 10, txt=f"Особисті якості: {user_data['qualities']}")

    pdf.output(pdf_path)

    document = FSInputFile(pdf_path, filename=f"{filename}.pdf")
    msg = await callback_query.message.answer_document(document, caption="✅ Ось твоє згенероване CV!")

    file_id = msg.document.file_id
    await add_cv(callback_query.from_user.id, cv_file_path=file_id)

    os.remove(pdf_path)
    return pdf_path

@router.message(F.text == "📝 Створити CV")
async def start_cv_form(message: types.Message, state: FSMContext):
    await message.answer("Почнемо з основної інформації:\n🔹 Ваше повне ім’я")
    await state.set_state(CVForm.full_name)

@router.message(CVForm.full_name)
async def ask_phone(message: types.Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    await message.answer("🔹 Номер телефону")
    await state.set_state(CVForm.phone)

@router.message(CVForm.phone)
async def ask_email(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await message.answer("🔹 Електронна пошта")
    await state.set_state(CVForm.email)

@router.message(CVForm.email)
async def ask_city(message: types.Message, state: FSMContext):
    await state.update_data(email=message.text)
    await message.answer("🔹 Місто проживання")
    await state.set_state(CVForm.city)

@router.message(CVForm.city)
async def ask_position(message: types.Message, state: FSMContext):
    await state.update_data(city=message.text)
    await message.answer("🔹 Яку посаду або сферу роботи ви шукаєте?")
    await state.set_state(CVForm.position)


@router.message(CVForm.position)
async def ask_education(message: types.Message, state: FSMContext):
    await state.update_data(position=message.text)
    await message.answer("🎓 Назва навчального закладу")
    await state.set_state(CVForm.education)

@router.message(CVForm.education)
async def ask_speciality(message: types.Message, state: FSMContext):
    await state.update_data(education=message.text)
    await message.answer("📘 Спеціальність")
    await state.set_state(CVForm.speciality)

@router.message(CVForm.speciality)
async def ask_education_years(message: types.Message, state: FSMContext):
    await state.update_data(speciality=message.text)
    await message.answer("📅 Роки навчання (від - до)")
    await state.set_state(CVForm.education_years)

@router.message(CVForm.education_years)
async def ask_certifications(message: types.Message, state: FSMContext):
    await state.update_data(education_years=message.text)
    await message.answer("✅ Додаткові сертифікати / курси (якщо маєте)")
    await state.set_state(CVForm.certifications)


@router.message(CVForm.certifications)
async def ask_company(message: types.Message, state: FSMContext):
    await state.update_data(certifications=message.text)
    await message.answer("💼 Назва компанії (якщо є досвід)")
    await state.set_state(CVForm.company)

@router.message(CVForm.company)
async def ask_job_title(message: types.Message, state: FSMContext):
    await state.update_data(company=message.text)
    await message.answer("🔹 Посада")
    await state.set_state(CVForm.job_title)

@router.message(CVForm.job_title)
async def ask_job_years(message: types.Message, state: FSMContext):
    await state.update_data(job_title=message.text)
    await message.answer("🔹 Роки роботи")
    await state.set_state(CVForm.job_years)

@router.message(CVForm.job_years)
async def ask_job_duties(message: types.Message, state: FSMContext):
    await state.update_data(job_years=message.text)
    await message.answer("🔹 Основні обов’язки на роботі")
    await state.set_state(CVForm.job_duties)


@router.message(CVForm.job_duties)
async def ask_tools(message: types.Message, state: FSMContext):
    await state.update_data(job_duties=message.text)
    await message.answer("🛠️ Якими програмами або інструментами вмієте користуватися?")
    await state.set_state(CVForm.tools)

@router.message(CVForm.tools)
async def ask_languages(message: types.Message, state: FSMContext):
    await state.update_data(tools=message.text)
    await message.answer("🌐 Знання мов (які і на якому рівні)")
    await state.set_state(CVForm.languages)

@router.message(CVForm.languages)
async def ask_other_skills(message: types.Message, state: FSMContext):
    await state.update_data(languages=message.text)
    await message.answer("🤹‍♂️ Які ще корисні навички маєте?")
    await state.set_state(CVForm.other_skills)


@router.message(CVForm.other_skills)
async def ask_about(message: types.Message, state: FSMContext):
    await state.update_data(other_skills=message.text)
    await message.answer("👤 Опишіть себе як працівника")
    await state.set_state(CVForm.about)

@router.message(CVForm.about)
async def ask_schedule(message: types.Message, state: FSMContext):
    await state.update_data(about=message.text)
    await message.answer("⏰ Який графік вам підходить?")
    await state.set_state(CVForm.schedule)


def confirmation_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Так", callback_data="yes")],
            [InlineKeyboardButton(text="Ні", callback_data="no")]
        ]
    )


@router.message(CVForm.schedule)
async def confirm_cv(message: types.Message, state: FSMContext):
    await state.update_data(schedule=message.text)
    data = await state.get_data()

    summary = "\n".join([f"• {key}: {value}" for key, value in data.items()])
    kb = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="Так"),types.KeyboardButton(text="Ні")]
        ],
        resize_keyboard=True
    )
    await message.answer(f"Ось що ти заповнив(ла):\n\n{summary}\n\nВсе правильно? (Так / Ні)",
    reply_markup=kb)
    await state.set_state(CVForm.confirm)

import json

@router.message(CVForm.confirm, F.text.in_(["Так", "Ні"]))
async def handle_confirmation(message: types.Message, state: FSMContext):
    if message.text == "Так":
        data = await state.get_data()
        await add_cv(
            user_id=message.from_user.id,
            cv_text=json.dumps(data, ensure_ascii=False)
        )

        await message.answer(
            "✅ Інформація збережена! Можеш завантажити своє CV або повернутись у меню.",
            reply_markup=main_menu_kb()
        )
        await state.clear()
    else:
        await message.answer("Окей, давай почнемо спочатку! 🔁", reply_markup=ReplyKeyboardRemove())
        await state.clear()
        await start_cv_form(message, state)
