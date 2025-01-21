from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram import Router, F

import request
from states import Categories

router = Router()


@router.message(Categories.category_name, F.text)
async def new_category_name(message: Message, state: FSMContext):
    new_cat_name = message.text
    if len(new_cat_name) > 20:
        new_cat_name = new_cat_name[:20]
    await request.add_category(new_cat_name, message.from_user.id)
    await state.clear()
    await message.answer(text="Категория добавлена")


@router.message(Categories.category_name)
async def new_category_name(message: Message):
    await message.answer(text="Это не текст, нужен ответ в текстовом формате")
