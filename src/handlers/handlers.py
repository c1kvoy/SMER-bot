from aiogram import Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup, \
    InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime

from sqlalchemy import select
from sqlalchemy import and_



from src.database import session, Diary, Users

router = Router()


class AddDiaryState(StatesGroup):
    time_period = State()
    situation = State()
    thought = State()
    emotion = State()
    reaction = State()


@router.message(Command("start"))
async def start(message: Message):
    smr_text = """
    🤍Добро пожаловать в дневник СМЭР!💙

    Бот напоминает вам оценивать свое эмоциональное состояние утром, днем и вечером с помощью смайликов: 😭🙁😐🙂🤩.
    Также Бот будет отправлять напоминания для заполнения непосредственно дневника СМЭР.

    ✍️Как заполнять дневник СМЭР?
    С (ситуация). Опишите ситуацию, которая вызвала противоречивые чувства и мысли, используя факты и избегая оценочных суждений. 
    М (мысль). Вспомните, какие мысли возникли у вас в голове во время проблемной ситуации.
    Э (эмоция). Зафиксируйте ваши эмоции и действия, которые за ними последовали. 
    Р (реакции). Запишите свои реакции на уровне тела (например, заколотилось сердце, вспотели руки) или/и своё поведение (кричал, хлопнул дверью).
    Делать записи в дневнике нужно хотя бы два-три раза в день в тот момент, когда вы испытываете выраженную негативную эмоцию, или как можно скорее после эпизода с ней

    Доступные вам команды: 

    /add - добавляет записи в ваш дневник СМЭР (Ситуация -> Мысль-> Эмоция -> Реакция) 
    /average - выводит среднюю оценку вашего настроения за сутки, неделю, месяц и советы от LLM системы по улучшению своего эмоционального состояния. 
    /export - экспорт вашего дневника в Excel 

    Все эти команды доступны вам в меню левой нижней части экрана.

    Спасибо, что заботитесь о своем здоровье!
    """
    await message.answer(
        smr_text
    )


@router.message(Command("add"))
async def start_add_entry(message: Message, state: FSMContext):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Утро")],
            [KeyboardButton(text="День")],
            [KeyboardButton(text="Вечер")]
        ],
        resize_keyboard=True
    )
    await message.answer("Выберите время дня для записи (утро, день, вечер):", reply_markup=keyboard)
    await state.set_state(AddDiaryState.time_period)


@router.message(AddDiaryState.time_period)
async def chose_period(message: Message, state: FSMContext):
    if message.text not in ["Утро", "День", "Вечер"]:
        await message.answer("Пожалуйста, выберите одно из значений: Утро, День или Вечер")
        return
    await state.update_data(time_period=message.text)
    await message.answer("Опишите ситуацию, которая произошла", reply_markup=ReplyKeyboardRemove())
    await state.set_state(AddDiaryState.situation)


@router.message(AddDiaryState.situation)
async def chose_situation(message: Message, state: FSMContext):
    await state.update_data(situation=message.text)
    await message.answer("Опишите о чем вы думали в данный момент")
    await state.set_state(AddDiaryState.thought)


@router.message(AddDiaryState.thought)
async def chose_thought(message: Message, state: FSMContext):
    await state.update_data(thought=message.text)
    await message.answer("Опишите эмоции которые вы ощущали в этот момент")
    await state.set_state(AddDiaryState.emotion)


@router.message(AddDiaryState.emotion)
async def chose_emotion(message: Message, state: FSMContext):
    await state.update_data(emotion=message.text)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="1.😭", callback_data="reaction_1")],
            [InlineKeyboardButton(text="2.🙁", callback_data="reaction_2")],
            [InlineKeyboardButton(text="3.😐", callback_data="reaction_3")],
            [InlineKeyboardButton(text="4.🙂", callback_data="reaction_4")],
            [InlineKeyboardButton(text="5.🤩", callback_data="reaction_5")]
        ]
    )

    await message.answer("Выберите свою реакцию от 1 до 5 смайликом", reply_markup=keyboard)
    await state.set_state(AddDiaryState.reaction)


@router.callback_query(lambda c: c.data.startswith("reaction_"))
async def handle_reaction(callback: CallbackQuery, state: FSMContext):
    reaction_map = {
        "reaction_1": 1,
        "reaction_2": 2,
        "reaction_3": 3,
        "reaction_4": 4,
        "reaction_5": 5
    }

    reaction = reaction_map.get(callback.data)
    if reaction is None:
        await callback.answer("Некорректный выбор.")
        return

    data = await state.get_data()
    data["reaction"] = reaction

    async with session() as db:
        query = select(Users).where(and_(Users.user_id == callback.from_user.id, Users.is_logged_in == True))
        result = await db.execute(query)
        user = result.scalars().first()

        if not user:
            await callback.message.answer("Вы не авторизованы.")
            return

        diary_entry = Diary(
            login=user.login,
            user_id=callback.from_user.id,
            time_period=data["time_period"],
            situation=data["situation"],
            reaction=data["reaction"],
            thoughts=data["thought"],
            emotions=data["emotion"],
            timestamp=datetime.now(),
        )
        db.add(diary_entry)
        await db.commit()

    await state.clear()
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        "Спасибо что поделились, запись добавлена в ваш дневник.",
        reply_markup=ReplyKeyboardRemove()
    )

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="/add")],
            [KeyboardButton(text="/average")],
            [KeyboardButton(text="/export")]
        ],
        resize_keyboard=True
    )
    await callback.message.answer(
        "Что вы хотите сделать дальше?",
        reply_markup=keyboard
    )