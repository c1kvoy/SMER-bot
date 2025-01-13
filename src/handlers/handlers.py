from aiogram import Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
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
    await message.answer(
        "Добро пожаловать в дневник СМЭР!\n\n"
        "Вы оцениваете свое состояние утром, днем и вечером с помощью смайликов: 😭🙁😐🙂🤩.\n"
        "Бот будет отправлять напоминания для заполнения дневника."
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
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="1.😭")],
            [KeyboardButton(text="2.🙁")],
            [KeyboardButton(text="3.😐")],
            [KeyboardButton(text="4.🙂")],
            [KeyboardButton(text="5.🤩")]
        ],
        resize_keyboard=True
    )
    await message.answer("Опишите свою реакцию от 1 до 5 смайликом", reply_markup=keyboard)
    await state.set_state(AddDiaryState.reaction)


@router.message(AddDiaryState.reaction)
async def chose_reaction(message: Message, state: FSMContext):
    hm = {"1.😭": 1, "2.🙁": 2, "3.😐": 3 ,"4.🙂": 4, "5.🤩":5}
    if message.text not in hm.keys():
        await message("Вы должны выбрать один из смайликов")
        return
    await state.update_data(reaction=hm[message.text])
    data = await state.get_data()
    async with session() as db:
        query = select(Users).where(and_(Users.user_id == message.from_user.id, Users.is_logged_in == True))
        result = await db.execute(query)
        user = result.scalars().first()

    diary_entry = Diary(
        login=user.login,
        user_id=message.from_user.id,
        time_period=data["time_period"],
        situation=data["situation"],
        reaction=data["reaction"],
        thoughts=data["thought"],
        emotions=data["emotion"],
        timestamp=datetime.now(),
    )
    await state.clear()
    async with session() as db:
        db.add(diary_entry)
        await db.commit()
    await message.answer(
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
    await message.answer(
        "Что вы хотите сделать дальше?",
        reply_markup=keyboard
    )


