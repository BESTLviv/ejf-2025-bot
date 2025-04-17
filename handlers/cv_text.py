from aiogram import Router, types, F
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove, KeyboardButton, ReplyKeyboardMarkup
from utils.database import add_cv

router = Router()

class CVForm(StatesGroup):
    name = State()
    contact = State()
    education = State()
    experience = State()
    skills = State()
    about = State()
    confirm = State()

@router.message(F.text == "📝 Створити резюме")
async def start_cv_form(message: types.Message, state: FSMContext):
    await message.answer(
        "Привіт! Щоб я міг(ла) створити для вас гарне резюме, мені потрібно кілька відповідей. Все просто 😊\n\n"
        "🔹 Ваше повне ім’я (українською та англійською, якщо потрібно)\n"
        "🔹 Номер телефону\n"
        "🔹 Електронна пошта (якщо маєте)\n"
        "🔹 Місто проживання\n"
        "🔹 Яку посаду або яку сферу роботи ви шукаєте?"
    )
    await state.set_state(CVForm.name)

@router.message(CVForm.name)
async def get_name_contact(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer(
        "Дякую! Тепер про вашу освіту:\n\n"
        "🎓 Назва навчального закладу\n"
        "📘 Спеціальність\n"
        "📅 Роки навчання (від - до)\n"
        "✅ Якщо маєте сертифікати або пройшли додаткові курси — напишіть, будь ласка, теж"
    )
    await state.set_state(CVForm.education)

@router.message(CVForm.education)
async def get_education(message: types.Message, state: FSMContext):
    await state.update_data(education=message.text)
    await message.answer(
        "Чудово, далі трохи про досвід:\n\n"
        "💼 Де ви працювали раніше (якщо маєте досвід)? Напишіть:\n"
        "🔹 Назву компанії\n"
        "🔹 Посаду\n"
        "🔹 Роки роботи\n"
        "🔹 Що ви робили / які були обов’язки"
    )
    await state.set_state(CVForm.experience)

@router.message(CVForm.experience)
async def get_experience(message: types.Message, state: FSMContext):
    await state.update_data(experience=message.text)
    await message.answer(
        "Супер! А тепер про ваші навички:\n\n"
        "🛠️ Якими програмами або інструментами вмієте користуватися?\n"
        "🌐 Знання мов — які і на якому рівні?\n"
        "🤹‍♂️ Які ще корисні навички маєте?"
    )
    await state.set_state(CVForm.skills)

@router.message(CVForm.skills)
async def get_skills(message: types.Message, state: FSMContext):
    await state.update_data(skills=message.text)
    await message.answer(
        "І останнє — трохи про вас особисто 😊\n\n"
        "👤 Опишіть себе як працівника (сильні сторони)\n"
        "⏰ Який графік вам підходить?"
    )
    await state.set_state(CVForm.about)

@router.message(CVForm.about)
async def confirm_cv(message: types.Message, state: FSMContext):
    await state.update_data(about=message.text)
    data = await state.get_data()

    preview = (
        f"🧾 Ось згенероване резюме:\n\n"
        f"👤 Ім’я: {data['name']}\n"
        f"🎓 Освіта: {data['education']}\n"
        f"💼 Досвід: {data['experience']}\n"
        f"🛠️ Навички: {data['skills']}\n"
        f"📄 Про себе: {data['about']}"
    )

    await message.answer(preview)
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✅ Все окей"), KeyboardButton(text="🔁 Заповнити наново")]
        ],
        resize_keyboard=True
    )
    await message.answer("Все вірно? 🤔", reply_markup=keyboard)
    await state.set_state(CVForm.confirm)

@router.message(CVForm.confirm)
async def finish_cv(message: types.Message, state: FSMContext):
    if message.text == "✅ Все окей":
        data = await state.get_data()
        user_id = message.from_user.id
        final_text = (
            f"👤 Ім’я: {data['name']}\n"
            f"🎓 Освіта: {data['education']}\n"
            f"💼 Досвід: {data['experience']}\n"
            f"🛠️ Навички: {data['skills']}\n"
            f"📄 Про себе: {data['about']}"
        )
        await add_cv(user_id=user_id, cv_text=final_text)
        await message.answer("✅ Готово! Ми зберегли твоє резюме 🧾", reply_markup=ReplyKeyboardRemove())
        await state.clear()
    elif message.text == "🔁 Заповнити наново":
        await message.answer("Окей, почнемо спочатку. Введи своє ім’я та контакти:", reply_markup=ReplyKeyboardRemove())
        await state.set_state(CVForm.name)
