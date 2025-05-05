from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from keyboards.registration_kb import get_course_kb, get_university_kb
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from keyboards.main_menu_kb import main_menu_kb 
from utils.database import save_user_data

router = Router()

class Registration(StatesGroup):
    name = State()
    course = State()
    university = State()
    speciality = State()

@router.message(F.text == "Старт 🚀")
async def start_registration(message: types.Message, state: FSMContext):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Звісно!")]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer(
        "📢 Інженерний Ярмарок Кар’єри — це місце, де ти зможеш познайомитися з топовими компаніями, дізнатись про вакансії, а також взяти участь у цікавих активностях.\n"
        "Тепер, познайомимося ближче!",
        reply_markup=keyboard
    )

@router.message(F.text == "Звісно!")
async def ask_name(message: types.Message, state: FSMContext):
    await message.answer(
        "Тоді почнімо! Напиши своє ім’я та прізвище у форматі:\n📌Максим Сеньків"
    )
    await state.set_state(Registration.name)

@router.message(Registration.name)
async def validate_name(message: types.Message, state: FSMContext):
    parts = message.text.strip().split()
    if len(parts) < 2:
        await message.answer("⚠️ Схоже, що дані введені неправильно. Будь ласка, спробуй ще раз!")
        return
    await state.update_data(name=message.text)
    await message.answer("Приємно познайомитись, {}! Тепер обери, на якому курсі ти навчаєшся: 📚".format(parts[0]),
                         reply_markup=get_course_kb())
    await state.set_state(Registration.course)

# @router.message(Registration.course)
# async def ask_university(message: types.Message, state: FSMContext):
#     await state.update_data(course=message.text)
    
#     if message.text in ["🔹 Не навчаюсь", "🔹 Ще у школі/коледжі"]:
#         await message.answer("Чудово, а як щодо спеціальності? Напиши назву свого фаху у форматі: СШІ/ІГДГ/ІБІС…")
#         await state.set_state(Registration.speciality)
#     else:
#         await message.answer("А в якому університеті?", reply_markup=get_university_kb())
#         await state.set_state(Registration.university)

# @router.message(Registration.university)
# async def ask_speciality(message: types.Message, state: FSMContext):
#     await state.update_data(university=message.text)
#     await message.answer("Чудово, а як щодо спеціальності? Напиши назву свого фаху у форматі: СШІ/ІГДГ/ІБІС…")
#     await state.set_state(Registration.speciality)

@router.message(Registration.course)
async def ask_university_or_finish(message: types.Message, state: FSMContext):
    await state.update_data(course=message.text)
    
    if message.text in ["🔹 Не навчаюсь", "🔹 Ще у школі/коледжі"]:
        data = await state.get_data()
        await save_user_data(
            user_id=message.from_user.id,
            name=data["name"],
            course=data["course"],
            university="Не вказано",
            speciality="Не вказано"
        )
        await message.answer(
            "Чудово, тебе зареєстровано. 🎉\n"
            "Зараз на панелі ти бачиш розділи – тисни на них, щоб дізнатись більше деталей про кожен блок 🔎.",
            reply_markup=main_menu_kb()
        )
        await state.clear()
    else:
        await message.answer("А в якому університеті?", reply_markup=get_university_kb())
        await state.set_state(Registration.university)

@router.message(Registration.university)
async def ask_speciality(message: types.Message, state: FSMContext):
    await state.update_data(university=message.text)
    await message.answer("Чудово, а як щодо спеціальності? Напиши назву свого фаху у форматі: СШІ/ІГДГ/ІБІС…")
    await state.set_state(Registration.speciality)

@router.message(Registration.speciality)
async def finish_registration(message: types.Message, state: FSMContext):
    await state.update_data(speciality=message.text)
    data = await state.get_data()

    await save_user_data(
        user_id=message.from_user.id,
        name=data["name"],
        course=data["course"],
        university=data["university"],
        speciality=data["speciality"]
    )
    await message.answer(
        "Чудово, тебе зареєстровано. 🎉\n"
        "Зараз на панелі ти бачиш розділи – тисни на них, щоб дізнатись більше деталей про кожен блок 🔎.",
         reply_markup=main_menu_kb() 
    )
    await state.clear()
