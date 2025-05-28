from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram import F
from keyboards.main_menu_kb import main_menu_kb
from aiogram import types, Router 
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, CallbackQuery,InputMediaPhoto
from aiogram.types.input_file import FSInputFile
import os
from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardRemove
from utils.database import db 
from aiogram.fsm.state import StatesGroup, State



router = Router()


@router.message(F.text == "Старт 🚀")
async def start_registration(message: types.Message, state: FSMContext):
    await message.answer(
        "📢 <b>Інженерний Ярмарок Кар’єри</b> — це місце, де ти зможеш познайомитися з топовими компаніями, дізнатись про вакансії, а також взяти участь у цікавих активностях.\n"
        "Тепер, познайомимося ближче!",
        parse_mode="HTML",
        reply_markup=main_menu_kb() 
    )
    await message.answer(
        "Зараз на панелі ти бачиш <b>розділи</b> – тисни на них, щоб дізнатись більше деталей про кожен блок 🔎.",
        parse_mode="HTML",
        reply_markup=main_menu_kb()
    )


from aiogram.types import FSInputFile

@router.message(F.text == "📅  Розклад")
async def show_schedule(message: types.Message):
    photo_path = "media/schedule.jpg"
    await message.answer_photo(
        photo=FSInputFile(photo_path),
        caption="<b>Ми створили <a href='https://calendar.google.com/calendar/u/0?cid=ZDFkN2Y2YWIwYTBhZTdkMGExNTYyMWMxYzFkMWFhMDg1NWE0MzM4ZDA0OTU5NzI0NjVmZDcxNGZlMTY5YzAxY0Bncm91cC5jYWxlbmRhci5nb29nbGUuY29t'>розклад</a> так, щоб ти міг повністю зануритись у кожну активність.</b>\n\n"
        "Використай цю можливість на максимум, та з нетерпінням чекаємо тебе!\n\n <b>Усі активності будуть проходити в 209 ауд. 4 Н.К.</b>",
        parse_mode="HTML"
    )





@router.message(F.text == "🎯 Гра Share and Win")
async def share_and_win(message: types.Message):
    await message.answer( "<b>Хочеш використати всі можливості ярмарку, запам’ятатись компаніям і виграти класні призи?</b>\n "
        "Тоді виконуй завдання в межах гри  “Share and Win” та ділися результатами у Stories! 📸\n\n"
        "⌛<b>Важливо!</b> Завдання потрібно опублікувати до <i>'15:30 29 травня'</i>. Пізніше вони не будуть зараховані.",
        parse_mode="HTML"
    )
    await message.answer( 
    "Завдання Share&Win \n\n"

    "📸 <b>Фото та соціальні мережі:</b>\n"
    "🔹 Відвідай інтерактив від <i>PWC Lviv SDC</i> і виклади фото з позначками @pwc_lviv_sdc та @best_lviv\n"
    "🔹 Зроби знімок з роботом від <i>Leoni</i> і поділись у соцмережах\n"
    "🔹 Сфотографуйся біля фотозони <i>Ukrsibbank</i> і відміть @ukrsibbank\n\n"

    "🧠 <b>Перевір свої знання:</b>\n"
    "🔹 Відповідай на питання від <i>Kevych Solutions</i>\n"
    "🔹 Зіграємо в інтелектуальну гру з <i>KPMG</i> – дай відповідь на їх запитання\n"
    "🔹 Згадай усе, що знаєш, – завдання від <i>Renesas</i>\n"
    "🔹 Покажи себе у відповіді на питання від <i>Coxit</i>\n"
    "🔹 Challenge accepted: питання від <i>Lifesaver</i>\n"
    "🔹 Не забудь виконати завдання від <i>Coax</i>\n\n"

    "🧩 <b>Інтерактиви та розвиток:</b>\n"
    "🔹 Візьми участь у веселому “Знайди свій soft skill” від <i>Clario Tech</i>\n"
    "🔹 Пройди опитування або kahoot від <i>GlobalLogic</i>\n"
    "🔹 Завітай на воркшоп від <i>Infineon</i> — гарантовано нові знання!\n",
    
    parse_mode="HTML"
)

    

@router.message(F.text == "👥 Чат з учасниками") # прибрав фотку 
async def chat_with_participants(message: types.Message):
    await message.answer(
        "<b>Доєднуйся до нашої спільноти та  ділися враженнями з іншими  учасниками</b>\n\nДля цього перейди за цим посиланням 👉 <b><a href='https://t.me/+-TS86G4tcoY0NTky'>Тик</a></b>",
        parse_mode="HTML"
    )




@router.message(F.text == "Я єблан")
async def chat_with_participants(message: types.Message):
    await message.answer("Я знаю")



file_ids = {} 

speakers = [
    {
        "name": "Денис Бігус",
        "photo_path": "media/bihus.png",
        "description": "🔹 Журналіст-розслідувач, засновник Bihus\n\n🔹 Сольний виступ «Як викривати корупцію та залишатись в живих»",
        "key": "bihus"
    },
    {
        "name": "Валентин Краснопльоров",
        "photo_path": "media/kapitalist.png",
        "description": "🔹 Засновник найвідомішого економічного YouTube каналу «Останній капіталіст»\n\n🔹 Фінансова грамотність. Чим раніше зрозумієш, тим більше шансів стати багатим в житті",
        "key": "kapitalist"
    },
     {
        "name": "Назар Тимошик",
        "photo_path": "media/tymoshyk.JPG",
        "description": "🔹 Засновник компанії UnderDefence\n\n🔹 Панельна дискусія «Що потрібно знати перед тим, як створювати власний продукт/компанію»",
        "key": "tymoshyk"
    },
    {
        "name": "Володимир Назаркевич",
        "photo_path": "media/kevych.png",
        "description": "🔹 Засновник і генеральний директор у Kevych Solutions\n\n🔹 Панельна дискусія «Що потрібно знати перед тим, як створювати власний продукт/компанію»",
        "key": "kevych"
    },
    {
        "name": "Віталій Якушев",
        "photo_path": "media/yakushev.png",
        "description": "🔹 Генеральний директор 10GUards\n\n🔹 Панельна дискусія «Що потрібно знати перед тим, як створювати власний продукт/компанію»",
        "key": "yakushev"
    },
    {
        "name": "Наталія Шаховська",
        "photo_path": "media/shakhovska.jpg",
        "description": "🔹 Ректор Національного університету «Львівська політехніка»\n\n🔹 Панельна дискусія «Робота після університету: чого не вистачає випускникам?»",
        "key": "shakhovska"
    },
    {
        "name": "Інна Шульгіна",
        "photo_path": "media/shulhina.jpg",
        "description": "🔹 Lead Recruirer в Sombra\n\n🔹 Панельна дискусія «Робота після університету: чого не вистачає випускникам?»",
        "key": "shulhina"
    },
    {
        "name": "Андрій Бойчук",
        "photo_path": "media/boichuk.jpg",
        "description": "🔹 Head of AI, викладач кафедри СШІ\n\n🔹 Панельна дискусія «Робота після університету: чого не вистачає випускникам?»",
        "key": "boichuk"
    },
    {
        "name": "Анна Сергійчук",
        "photo_path": "media/serhiichuk.jpg",
        "description": "🔹 Talent Acquisition Partner з більш як 7-річним досвідом у рекрутингу (в тому числі продуктових компаніях Ajax Systems, SKELAR)\n\n🔹 Панельна дискусія «Робота після університету: чого не вистачає випускникам?»",
        "key": "serhiichuk"
    },
    {
        "name": "Андрій Сергійчук",
        "photo_path": "media/andrewkha.png",
        "description": "🔹 Модератор\n\n🔹 HR Generalist у Kevych Solutions\n\n🔹Панельна дискусія «Робота після університету: чого не вистачає випускникам?»",
        "key": "andrewkha"
    }
]

def build_speaker_keyboard(selected_index: int):
    kb = InlineKeyboardBuilder()
    for i, speaker in enumerate(speakers):
        name = speaker["name"]
        if i == selected_index:
            text = f"▶️{name}◀️"
        else:
            text = name
        kb.add(InlineKeyboardButton(text=text, callback_data=f"select_speaker:{i}"))
    return kb.adjust(1).as_markup()

@router.message(F.text == "🗣️ Спікери") # прибрав фотку спікерів 
async def show_speakers(message: types.Message):
    await message.answer("<b>Найцінніше, що можна зробити з набутими знаннями — це застосовувати їх і ділитися з іншими.</b> Наші спікери готові передати свою мудрість, тож приймай її та розширюй горизонти!",
                               parse_mode="HTML"
    )
    selected_index = 0
    speaker = speakers[selected_index]
    photo = FSInputFile(speaker["photo_path"])
    keyboard = build_speaker_keyboard(selected_index)

    msg = await message.answer_photo(
        photo=photo,
        caption=f"<b>{speaker['name']}</b>\n\n{speaker['description']}",
        reply_markup=keyboard,
        parse_mode="HTML"
    )

    file_ids[speaker["key"]] = msg.photo[-1].file_id

@router.callback_query(F.data.startswith("select_speaker:"))
async def select_speaker(callback: CallbackQuery):
    selected_index = int(callback.data.split(":")[1])
    speaker = speakers[selected_index]
    keyboard = build_speaker_keyboard(selected_index)

    file_id = file_ids.get(speaker["key"])
    if not file_id:
        file = FSInputFile(speaker["photo_path"])
        msg = await callback.message.answer_photo(
            photo=file,
            caption=f"<b>{speaker['name']}</b>\n\n{speaker['description']}",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        file_ids[speaker["key"]] = msg.photo[-1].file_id
        await callback.message.delete()
    else:
        media = InputMediaPhoto(
            media=file_id,
            caption=f"<b>{speaker['name']}</b>\n\n{speaker['description']}" ,
            parse_mode="HTML"
        )
        await callback.message.edit_media(media=media, reply_markup=keyboard)

    await callback.answer()

@router.message(F.text == "🩵💛 Підтримка ЗСУ")
async def show_ukraine_support(message: types.Message):
    await message.answer(
        "<b>Завдяки нашим військовим ми можемо організовувати Інженерний Ярмарок Кар’єри.</b>\n\n"
        "Тепер наш час віддячити їм – долучайся до <b>збору</b> 👇",
        parse_mode="HTML"
    )

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
    photo = FSInputFile(photo_path)
    await message.answer_photo(
        photo=photo,
        caption=caption,
        parse_mode="HTML"
    )

def rating_keyboard():
    keyboard = [
        [InlineKeyboardButton(text="⭐ 1 – Не сподобалось", callback_data="rate_1")],
        [InlineKeyboardButton(text="⭐ 2 – Могло бути краще", callback_data="rate_2")],
        [InlineKeyboardButton(text="⭐ 3 – Було нормально", callback_data="rate_3")],
        [InlineKeyboardButton(text="⭐ 4 – Було круто!", callback_data="rate_4")],
        [InlineKeyboardButton(text="⭐ 5 – Неймовірно, чекаю наступний ІЯК!", callback_data="rate_5")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


@router.message(F.text == "💬 Відгуки події")
async def ask_for_feedbacks(message: types.Message):
    await message.answer("💬 Залишити відгук можна буде в другий <b>день Ярмарку</b>, 29 травня.\nПовертайся до цієї кнопки трохи згодом — нам дуже важлива твоя думка!",
                         parse_mode="HTML")

# class FeedbackStates(StatesGroup):# всі штуки з фідбеками
#     waiting_for_comment = State()
# @router.message(F.text == "💬 Відгуки події")
# async def start_feedback(message: types.Message, state: FSMContext):
#     await state.clear()  # Очистити попередні стани на всякий випадок
#     await message.answer(
#         "Це були два неймовірні дні! Ми намагалися зробити <b>Інженерний Ярмарок Карʼєри</b> якомога кориснішим і цікавим для тебе. А тепер твоя черга допомогти нам стати кращими! Оціни, будь ласка, захід від 1 до 5 📊.",
#         parse_mode="HTML",
#         reply_markup=rating_keyboard()
#     )
# @router.callback_query(F.data.startswith("rate_"))
# async def handle_rating(callback: CallbackQuery, state: FSMContext):
#     rating = int(callback.data.split("_")[1])
#     await state.update_data(rating=rating)

#     await callback.message.edit_text(
#         "🙏 Дякуємо за оцінку!\nНам дуже важливо почути твою думку. Напиши, що тобі сподобалось, а що можна покращити – адже саме твій відгук спонукає нас до розвитку!",
#         parse_mode="HTML",
#         reply_markup=None
#     )
#     await state.set_state(FeedbackStates.waiting_for_comment)
# @router.message(FeedbackStates.waiting_for_comment)
# async def save_feedback(message: types.Message, state: FSMContext):
#     user_id = message.from_user.id
#     comment = message.text
#     data = await state.get_data()
#     rating = data.get('rating')

#     feedback_collection = db["feedbacks"]
#     await feedback_collection.update_one(
#         {"telegram_id": user_id},
#         {"$set": {
#             "telegram_id": user_id,
#             "rating": rating,
#             "comment": comment
#         }},
#         upsert=True
#     )

#     await message.answer(
#         "Дуже дякуємо! Твої відповіді допоможуть нам рухатися у правильному напрямку.\n\n"
#         "Хочемо нагадати, що <b>Інженерний Ярмарок Кар’єри</b> став можливим завдяки студентській організації <b>BEST Lviv</b>. Ми створюємо й інші круті події, які можуть тебе зацікавити:\n\n"
#         "🟣 <b>BEST Training Week</b> – тиждень лекцій від спікерів;\n"
#         "🔴 <b>BEST Capture The Flag</b> – командні змагання з кібербезпеки;\n"
#         "🟠 <b>BEST Engineering Competition</b> – інженерні змагання;\n"
#         "🟢 <b>BEST::HACKath0n</b> – 24-годинні IT-змагання;\n"
#         "Усі ці заходи є <b>безкоштовними</b>, тож слідкуй за нашими соцмережами та долучайся до інших подій, які зацікавили! 🎯",
#         parse_mode="HTML",
#         reply_markup=main_menu_kb()
#     )
#     await state.clear()
