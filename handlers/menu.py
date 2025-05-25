from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram import F
from keyboards.main_menu_kb import main_menu_kb
from aiogram import types, Router 
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, CallbackQuery,InputMediaPhoto
from aiogram.types.input_file import FSInputFile
import os


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
        caption="<b>Ми створили <a href='https://ejf.best-lviv.org.ua/schedule'>розклад</a> так, щоб ти міг повністю зануритись у кожну активність.</b>\n\n"
        "Використай цю можливість на максимум, та з нетерпінням чекаємо тебе!",
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
        "<b>Завдання Share&Win</b>\n\n"
        "Відвідай будь-яку інформаційну зону, зроби фото та виклади в Instagram Stories із тегами <a href='https://www.instagram.com/best_lviv/'>@best_lviv</a> та компанії-учасника (компанії-учасники не можуть повторюватись).\n\n"
        "Надішли CV в телеграм-бот ярмарку\n\n"
        "Відвідай воркшоп та поділись цим соцмережах, відзначивши <a href='https://www.instagram.com/best_lviv/'>@best_lviv</a> і спікера.\n\n"
        "Відвідай панельну дискусію та поділись цим соцмережах, відмітивши <a href='https://www.instagram.com/best_lviv/'>@best_lviv</a> і учасників дискусії.\n\n"
        "Випробуй свої сили на симуляції співбесід, попередньо зареєструвавшись в телеграм боті Ярмарку.\n\n"
        "Відвідай лекцію, постав питання спікеру та поділися відповіддю в Instagram Stories, відмітивши <a href='https://www.instagram.com/best_lviv/'>@best_lviv</a> і спікера.\n\n"
        "Запиши 3 ключові ідеї з панельної дискусії та поділися ними в Stories, відмітивши <a href='https://www.instagram.com/best_lviv/'>@best_lviv</a> і учасників дискусії.\n\n"
        "Знайди головний банер події, зроби фото та виклади його у Stories, відмітивши <a href='https://www.instagram.com/best_lviv/'>@best_lviv</a>.\n\n"
        "Пройдися по виставковій зоні, знайди найкреативніший стенд (на твій погляд), зроби фото та відміть <a href='https://www.instagram.com/best_lviv/'>@best_lviv</a> і компанію.\n\n"
        "Знайди стенд компанії, яка проводить тестові завдання, виконай його та поділись результатами у Stories з тегами @best_lviv і компанії.\n\n",
        parse_mode="HTML")
    

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
        "description": "🔹 Засновник найвідомішого економічного YouTube каналу «Останній капіталіст»\n\n🔹 Сольний виступ «Фінансова грамотність для студентів: як не жити від стипендії до стипендії»",
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
@router.message(F.text == "💬 Відгуки події")
async def ask_for_feedbacks(message: types.Message):
    await message.answer("💬 Залишити відгук можна буде в другий <b>день Ярмарку</b>, 29 травня.\nПовертайся до цієї кнопки трохи згодом — нам дуже важлива твоя думка!",
                         parse_mode="HTML")
