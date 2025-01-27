from aiogram import Router
from aiogram.types.callback_query import CallbackQuery
from aiogram.fsm.context import FSMContext

import request
from states import Categories

router = Router()

@router.callback_query(Categories.delete_cat)
async def del_category(callback: CallbackQuery, state: FSMContext):
    cat_id = int(callback.data.split('_')[-1])
    cat_name = await request.get_category_name_from_category_id(cat_id)
    if cat_name.strip() == 'Прочее':
        await callback.answer('Ошибка')
        await callback.message.answer(text = f"Эту категорию удалить невозможно!")
        await state.clear()
        return
    await callback.answer('Категория выбрана!')
    other_cat_id = await request.get_cat_id_from_cat_name(callback.from_user.id, 'Прочее')
    await request.transger_all_expenses_to_other_cat(cat_id, other_cat_id)
    await request.delete_category(cat_id)
    await state.clear()
    await callback.message.answer(text = f"Категория {cat_name} успешно удалена")
