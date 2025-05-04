from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from utils.database import add_cv
from keyboards.cv_kb import get_cv_type_kb
from states.cv import CVForm

router = Router()

@router.message(F.text == "📂 CV")
async def start_cv_menu(message: types.Message):
    await message.answer(
        "Компанії шукають різних спеціалістів саме серед учасників Ярмарку!\n"
        "Тож завантажуй своє резюме у форматі PDF та чекай дзвіночка!\n\n"
        "Не маєш CV? Я допоможу – відповідай на декілька запитань, і за кілька хвилин матимеш готове резюме!",
        reply_markup=get_cv_type_kb()
    )

@router.message(F.document)
async def handle_cv_file(message: types.Message):
    if message.document.mime_type != "application/pdf":
        await message.answer("❗Упс, схоже, що формат файлу неправильний. Спробуй ще раз, використовуючи PDF")
        return

    file_id = message.document.file_id
    await add_cv(message.from_user.id, cv_file_path=file_id)
    await message.answer("✅ CV завантажено! Ти красень! 🎉")

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

@router.message(CVForm.schedule)
async def confirm_cv(message: types.Message, state: FSMContext):
    await state.update_data(schedule=message.text)
    data = await state.get_data()

    summary = "\n".join([f"• {key}: {value}" for key, value in data.items()])
    await message.answer(f"Ось що ти заповнив(ла):\n\n{summary}\n\nВсе правильно? (Так / Ні)")
    await state.set_state(CVForm.confirm)
def confirmation_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Так", callback_data="yes")],
            [InlineKeyboardButton(text="Ні", callback_data="no")]
        ]
    )

@router.message(CVForm.confirm)
async def handle_confirmation(message: types.Message, state: FSMContext):
    await message.answer(
        "Ти впевнений(а), що хочеш згенерувати своє CV з цієї інформації?\n"
        "Якщо так, натисни 'Так', якщо хочеш почати спочатку, натисни 'Ні'.",
        reply_markup=confirmation_kb()  
    )

@router.callback_query(F.data == "yes")
async def confirm_cv(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await add_cv(user_id=callback_query.from_user.id, cv_text=str(data))  
    await callback_query.answer("✅ Готово! Ми згенерували твоє CV та зберегли його 💾")
    await callback_query.message.edit_reply_markup(reply_markup=None)  
    await state.clear()

@router.callback_query(F.data == "no")
async def restart_cv(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer("Окей, давай почнемо спочатку! 🔁")
    await callback_query.message.edit_reply_markup(reply_markup=None)  
    await state.clear()
    await start_cv_form(callback_query.message, state)  