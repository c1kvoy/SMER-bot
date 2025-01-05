from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from src.database import session, Users

router = Router()

class RegistrationStates(StatesGroup):
    waiting_for_first_name = State()
    waiting_for_last_name = State()

@router.message(Command("register"))
async def start_registration(message: Message, state: FSMContext):
    await message.answer("Пожалуйста, введите ваше имя:")
    await state.set_state(RegistrationStates.waiting_for_first_name)

@router.message(RegistrationStates.waiting_for_first_name)
async def process_first_name(message: Message, state: FSMContext):
    first_name = message.text.strip()
    await state.update_data(first_name=first_name)
    await message.answer("Теперь введите вашу фамилию:")
    await state.set_state(RegistrationStates.waiting_for_last_name)

@router.message(RegistrationStates.waiting_for_last_name)
async def process_last_name(message: Message, state: FSMContext):
    last_name = message.text.strip()
    data = await state.get_data()
    first_name = data["first_name"]

    async with session() as db:
        existing_user = await db.get(Users, message.from_user.id)
        if not existing_user:
            new_user = Users(
                user_id=message.from_user.id,
                first_name=first_name,
                last_name=last_name
            )
            db.add(new_user)
            await db.commit()

            await message.answer(
                f"Спасибо, {first_name} {last_name}! Вы успешно зарегистрированы."
            )
        else:
            await message.answer("Вы уже зарегистрированы.")

    await state.clear()