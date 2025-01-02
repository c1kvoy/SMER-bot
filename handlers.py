from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from datetime import datetime
from database import session, Diary
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

