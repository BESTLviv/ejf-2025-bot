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
        "📢 Інженерний Ярмарок Кар’єри — це місце, де ти зможеш познайомитися з топовими компаніями, дізнатись про вакансії, а також взяти участь у цікавих активностях.\n"
        "Тепер, познайомимося ближче!",
        reply_markup=main_menu_kb() 
    )
    await message.answer(
        "Зараз на панелі ти бачиш розділи – тисни на них, щоб дізнатись більше деталей про кожен блок 🔎.",
        reply_markup=main_menu_kb()
    )


from aiogram.types import FSInputFile

@router.message(F.text == "📅  Розклад")
async def show_schedule(message: types.Message):
    photo_path = "media/schedule.jpg"
    await message.answer_photo(
        photo=FSInputFile(photo_path),
        caption="Ми створили <a href='https://ejf.best-lviv.org.ua/schedule'>розклад</a> так, щоб ти міг повністю зануритись у кожну активність. "
        "Використай цю можливість на максимум, та з нетерпінням чекаємо тебе!",
        parse_mode="HTML"
    )





@router.message(F.text == "🎯 Гра Share and Win")
async def share_and_win(message: types.Message):
    photo_path = "media/shareandwin.jpg"
    caption = (
        "Хочеш використати всі можливості ярмарку, запам’ятатись компаніям і виграти класні призи? "
        "Тоді виконуй завдання в межах гри  “Share and Win” та ділися результатами у Stories! 📸\n\n"
        "⌛<b>Важливо!</b> Завдання потрібно опублікувати до <i>'15:30 29 травня'</i>. Пізніше вони не будуть зараховані."
    )
    await message.answer_photo(
        photo=FSInputFile(photo_path),
        caption=caption,
        parse_mode="HTML"
    )
    await message.answer(
        "Відвідай будь-яку інформаційну зону, зроби фото та виклади в Instagram Stories із тегами <a href='https://www.instagram.com/best_lviv/'>@best_lviv</a> та компанії-учасника (компанії-учасники не можуть повторюватись).\n\n", 
        "Надішли CV в телеграм-бот ярмарку\n\n",
        "Відвідай воркшоп та поділись цим соцмережах, відзначивши <a href='https://www.instagram.com/best_lviv/'>@best_lviv</a> і спікера.\n\n",
        "Відвідай панельну дискусію та поділись цим соцмережах, відмітивши <a href='https://www.instagram.com/best_lviv/'>@best_lviv</a> і учасників дискусії.\n\n", 
        "Випробуй свої сили на симуляції співбесід, попередньо зареєструвавшись в телеграм боті Ярмарку.\n\n",
        "Відвідай лекцію, постав питання спікеру та поділися відповіддю в Instagram Stories, відмітивши <a href='https://www.instagram.com/best_lviv/'>@best_lviv</a> і спікера.\n\n",
        "Запиши 3 ключові ідеї з панельної дискусії та поділися ними в Stories, відмітивши <a href='https://www.instagram.com/best_lviv/'>@best_lviv</a> і учасників дискусії.\n\n",
        "Знайди головний банер події, зроби фото та виклади його у Stories, відмітивши <a href='https://www.instagram.com/best_lviv/'>@best_lviv</a>.\n\n",
        "Пройдися по виставковій зоні, знайди найкреативніший стенд (на твій погляд), зроби фото та відміть <a href='https://www.instagram.com/best_lviv/'>@best_lviv</a> і компанію.\n\n",
        "Знайди стенд компанії, яка проводить тестові завдання, виконай його та поділись результатами у Stories з тегами @best_lviv і компанії.\n\n", 
        parse_mode="HTML"
        )
    

@router.message(F.text == "👥 Чат з учасниками")
async def chat_with_participants(message: types.Message):
    photo_path = "media/chat.jpg"
    caption = ("Доєднуйся до нашої спільноти та  ділися враженнями з іншими  учасниками. Для цього перейди за цим посиланням 👉 https://t.me/bestlviv")
    await message.answer_photo(
        photo=FSInputFile(photo_path),
        caption=caption,
        parse_mode="HTML"
    )




@router.message(F.text == "Я єблан")
async def chat_with_participants(message: types.Message):
    await message.answer("Я знаю")



file_ids = {} 

speakers = [
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

@router.message(F.text == "🗣️ Спікери")
async def show_speakers(message: types.Message):
    photo_path = "media/speakers.jpg"
    caption = ("Найцінніше, що можна зробити з набутими знаннями — це застосовувати їх і ділитися з іншими. Наші спікери готові передати свою мудрість, тож приймай її та розширюй горизонти!")
    await message.answer_photo(
        photo=FSInputFile(photo_path),
        caption=caption)
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
    zsu_photo_path = "media/armedforces.jpg"
    zsu_caption = (
        "Завдяки нашим військовим ми можемо організовувати Інженерний Ярмарок Кар’єри. "
        "Тепер наш час віддячити їм – долучайся до збору 👇"
    )
    zsu_photo = FSInputFile(zsu_photo_path)
    await message.answer_photo(
        photo=zsu_photo,
        caption=zsu_caption,
        parse_mode="HTML"
    )

    photo_path = "media/zbir.jpg"
    caption = (
        "РОЗІГРАШ🔥\n\n"
        "Завжди пам'ятаймо: війна торкається кожного з нас. Ми не маємо ані часу, ані морального права зупинятись чи розслаблятись. Нещодавно BEST Lviv успішно завершив попередній збір, і тепер ми готові оголосити новий — ще один крок до спільної перемоги.\n\n"
        "📢 Продовжуємо підтримувати 103 окрему бригаду ТРО, яка зараз героїчно захищає нас на Сумському напрямку, а також групу керування польотами одного із аеродромів України.\n\n"
        "🔋 Збираємо на Ecoflow Delta max 2000, а також на бінокль Celestron SkyMaster Pro\n\n"
        "⚔️ Наша ціль: 60 000 грн\n\n"
        "Посилання на банку знаходиться в шапці профілю.\n\n"
        "💳 Номер картки банку:<code> 4441 1111 2343 2472</code>\n\n"
        "🫂 Просимо кожного — задонатьте й поширте серед друзів. Кожна гривня наближає перемогу! Також щоб підняти вам мотивацію – розігруємо шеврон за донат від 50 грн. Щоб виграти його, вкажіть ваш контакт у коментарі до донату.\n\n"
        "Усі звіти будуть опубліковані на сторінці <a href='https://www.instagram.com/p/DIloK3-gU4t/?img_index=1'>@best_lviv</a>."
    )
    photo = FSInputFile(photo_path)
    await message.answer_photo(
        photo=photo,
        caption=caption,
        parse_mode="HTML"
    )
