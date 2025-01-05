import os
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile, ReplyKeyboardMarkup, KeyboardButton
from src.utils.export import export_to_excel

router = Router()

@router.message(Command("export"))
async def handle_export(message: Message):
    user_id = message.from_user.id
    try:
        filepath = await export_to_excel(user_id)
        file = FSInputFile(filepath)
        await message.answer_document(file, caption="Ваш экспорт дневника готов!")
        os.remove(filepath)
    except Exception as e:
        await message.answer("Произошла ошибка при экспорте данных. Попробуйте позже.")
        print(f"Ошибка при экспорте данных: {e}")
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