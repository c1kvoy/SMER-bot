from aiogram import Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from src.database import session, Users
from sqlalchemy.future import select
from sqlalchemy import and_

router = Router()


class RegistrationStates(StatesGroup):
    waiting_for_login = State()
    waiting_for_password = State()


@router.message(Command("register"))
async def start_registration(message: Message, state: FSMContext):
    await message.answer("Пожалуйста, введите ваш логин:")
    await state.set_state(RegistrationStates.waiting_for_login)


@router.message(RegistrationStates.waiting_for_login)
async def process_login(message: Message, state: FSMContext):
    login = message.text.strip()
    if message.text[0] == "/": return
    async with session() as db:
        query = select(Users).where(Users.login == login)
        result = await db.execute(query)
        existing_user = result.scalars().first()

    if existing_user:
        await message.answer("Этот логин уже используется. Пожалуйста, выберите другой.")
        return

    await state.update_data(login=login)
    await message.answer("Теперь введите ваш пароль:")
    await state.set_state(RegistrationStates.waiting_for_password)


@router.message(RegistrationStates.waiting_for_password)
async def process_password(message: Message, state: FSMContext):
    password = message.text.strip()
    data = await state.get_data()
    login = data["login"]

    async with session() as db:
        new_user = Users(
            user_id=message.from_user.id,
            login=login,
            password=password
        )
        db.add(new_user)
        await db.commit()

    await message.answer(f"Спасибо, {login}! Вы успешно зарегистрированы.")
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
    await state.clear()


@router.message(Command("logout"))
async def handle_logout(message: Message):
    user_id = message.from_user.id

    async with session() as db:
        query = select(Users).where(and_(Users.user_id == user_id, Users.is_logged_in == True))
        result = await db.execute(query)
        user = result.scalars().first()

        if user:
            user.is_logged_in = False
            await db.commit()
            await message.answer("Вы успешно вышли из системы.")
        else:
            await message.answer("Вы не авторизованы.")

class LoginStates(StatesGroup):
    waiting_for_login = State()
    waiting_for_password = State()


@router.message(Command("login"))
async def start_login(message: Message, state: FSMContext):
    async with session() as db:
        query = select(Users).where(and_(Users.user_id == message.from_user.id, Users.is_logged_in == True))
        result = await db.execute(query)
        user = result.scalars().first()
        if user:
            await message.answer("Вы уже залогинены, можете, если хотите выйти пропишите /logout:")
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
    await message.answer("Введите ваш логин:")
    await state.set_state(LoginStates.waiting_for_login)

@router.message(LoginStates.waiting_for_login)
async def process_login(message: Message, state: FSMContext):
    login = message.text.strip()

    async with session() as db:
        query = select(Users).where(Users.login == login)
        result = await db.execute(query)
        user = result.scalars().first()

    if user:
        await state.update_data(user_id=user.user_id, login=login)
        await message.answer("Введите ваш пароль:")
        await state.set_state(LoginStates.waiting_for_password)
    else:
        await message.answer("Логин не найден. Попробуйте снова или зарегистрируйтесь с помощью команды /register.")
        await state.clear()

@router.message(LoginStates.waiting_for_password)
async def process_password(message: Message, state: FSMContext):
    password = message.text.strip()
    data = await state.get_data()

    login = data["login"]

    async with session() as db:
        query = select(Users).where(Users.login == login)
        result = await db.execute(query)
        user = result.scalars().first()

        if user and user.password == password:
            user.is_logged_in = True
            await db.commit()
            await message.answer("Вы успешно вошли в систему.")
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
        else:
            await message.answer("Неверный пароль. Попробуйте снова или зарегистрируйтесь с помощью команды /register.")
            await state.clear()