from aiogram import Router, F
from aiogram.types import Message
from aiogram.types.callback_query import CallbackQuery
from aiogram.fsm.context import FSMContext

import request
from states import Categories

router = Router()


@router.callback_query(Categories.edit_cat)
async def get_category_to_edit(callback: CallbackQuery, state: FSMContext):
    cat_id = int(callback.data.split('_')[-1])
    cat_name = await request.get_category_name_from_category_id(cat_id)
    if cat_name == 'Прочее':
        await callback.answer('Ошибка!')
        await callback.message.answer(text = f"Эту категорию переименовать невозможно!")
        await state.clear()
        return
    await callback.answer('Категория выбрана')
    await state.update_data(cat_id = cat_id)
    await callback.message.answer(text = f"Введите новое имя для категории: ")


@router.message(Categories.edit_cat, F.text)
async def get_new_cat_name(message: Message, state: FSMContext):
    new_cat_name = message.text
    if new_cat_name.strip() == 'Прочее':
        await message.answer("Такое название использовать нельзя!")
        return
    if len(new_cat_name) > 20:
        new_cat_name = new_cat_name[:20]
    await request.change_cat_name(await state.get_value('cat_id'), new_cat_name)
    await message.answer(f"Имя успешно изменено на {new_cat_name}")
    await state.clear()


@router.message(Categories.edit_cat)
async def get_new_cat_name(message: Message):
    await message.answer("Сообщение не распознано как текст, пожалуйста, попробуйте снова")
    