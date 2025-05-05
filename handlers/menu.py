from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram import F
from keyboards.main_menu_kb import main_menu_kb


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
    caption = (
        "Ми створили <a href='https://ejf.best-lviv.org.ua/schedule'>розклад</a> так, щоб ти міг повністю зануритись у кожну активність. "
        "Використай цю можливість на максимум, та з нетерпінням чекаємо тебе!"
    )
    photo = FSInputFile(photo_path)
    await message.answer_photo(
        photo=photo,
        caption=caption,
        parse_mode="HTML"
    )

@router.message(F.text == "📂 СV")
async def show_cv(message: types.Message):
    await message.answer("Завантажте своє резюме або створіть його за допомогою бота. Що ви хочете зробити? 📄")

@router.message(F.text == "🎯 Гра Share and Win")
async def share_and_win(message: types.Message):
    await message.answer("Хочеш використати всі можливості ярмарку, запам’ятатись компаніям і виграти класні призи? Тоді виконуй завдання в межах гри  “Share and Win” та ділися результатами у Stories! 📸")
    photo_path = "media/shareandwin.jpg"
    await message.answer_photo(
        photo=FSInputFile(photo_path),  
        parse_mode="HTML"
    )


@router.message(F.text == "👥 Чат з учасниками")
async def chat_with_participants(message: types.Message):
    await message.answer("Доєднуйся до нашої спільноти та  ділися враженнями з іншими  учасниками. Для цього перейди за цим посиланням 👉 https://t.me/bestlviv")

@router.message(F.text == "🗣️ Спікери")
async def show_speakers(message: types.Message):
    await message.answer("Тут буде список спікерів на Ярмарку. Бажаєте дізнатись більше про спікерів? 👨‍🏫")

@router.message(F.text == "🩵💛 Підтримка ЗСУ")
async def show_ukraine_support(message: types.Message):
    await message.answer("Завдяки нашим військовим ми можемо організовувати Інженерний Ярмарок Кар’єри. Тепер наш час віддячити їм – долучайся до збору  👇")
    photo_path = "media/zbir.jpg"
    caption = (
        "РОЗІГРАШ🔥\n\n"
        "Завжди пам'ятаймо: війна торкається кожного з нас. Ми не маємо ані часу, ані морального права зупинятись чи розслаблятись. Нещодавно BEST Lviv успішно завершив попередній збір, і тепер ми готові оголосити новий — ще один крок до спільної перемоги.\n\n"
        "📢 Продовжуємо підтримувати 103 окрему бригаду ТРО, яка зараз героїчно захищає нас на Сумському напрямку, а також групу керування польотами одного із аеродромів України.\n\n"
        "🔋 Збираємо на Ecoflow Delta max 2000, а також на бінокль Celestron SkyMaster Pro\n\n"
        "⚔️ Наша ціль: 60 000 грн\n\n"
        "Посилання на банку знаходиться в шапці профілю.\n\n"
        "💳 Номер картки банку:<code> 4441 1111 2343 2472</code>\n\n"
        "🫂 Просимо кожного — задонатьте й поширте серед друзів. Кожна гривня наближає перемогу! Також щоб підняти вам мотивацію – розігруємо шеврон за донат від 50 грн. Щоб виграти його, вкажіть ваш контанкт у коментарі до донату.\n\n"
        "Усі звіти будуть опубліковані на сторінці <a href='https://www.instagram.com/p/DIloK3-gU4t/?img_index=1'>@best_lviv</a>."
    )
    photo = FSInputFile(photo_path)
    await message.answer_photo(
        photo=photo,
        caption=caption,
        parse_mode="HTML"
    )
