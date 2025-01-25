from aiogram.fsm.context import FSMContext

import keyboard as kb
import request
from states import Expenses
import lists_messages_constructor as lmr


async def show_by_category(callback, st: Expenses, state: FSMContext):
    cat_dict = await request.get_categories(callback.from_user.id)
    cat_buttons = await kb.create_cat_kb(cat_dict)
    await callback.message.answer(text = 'Выберите категорию расходов', reply_markup = cat_buttons)
    await state.set_state(st)


async def show_all(callback, keyword, state: FSMContext):
    exp_list = await request.get_list_of_all_expenses_in_one_query(callback.message.chat.id)
    exp_text, pages_kb = await lmr.message_constructor(page=1, show_cat=True, cat_id=None, tg_id=callback.message.chat.id)
    await callback.message.answer(text = exp_text, reply_markup=pages_kb)
    await callback.message.answer(text = f'Введите номер расхода, который хотите {keyword}:')
    await state.update_data(sorted_exp_list = exp_list)


async def choose_num_from_cat(callback, keyword, st: Expenses, state: FSMContext):
    await callback.answer('Список готов!')
    cat_id = int(callback.data.split('_')[-1])
    exp_list = await request.get_list_of_expenses_from_category_id(cat_id)
    if exp_list:
        exp_text, pages_kb = await lmr.message_constructor(page=1, show_cat=False, cat_id=cat_id, tg_id=callback.message.chat.id)
    else:
        exp_text = await lmr.message_constructor(page=1, show_cat=False, cat_id=cat_id, tg_id=callback.message.chat.id)
        pages_kb = None    
    await callback.message.answer(text = exp_text, reply_markup=pages_kb)
    if pages_kb:
        await callback.message.answer(text = f'Введите номер расхода, который хотите {keyword}:')
    await state.set_state(st)
    await state.update_data(sorted_exp_list = exp_list)


async def filter_num(message, state):
    try:
        num = int(message.text)
    except:
        await message.answer(text='Это не число, попробуйте снова!')
        return
    if num > 0 and num <= len(await state.get_value('sorted_exp_list')):
        exp_to_edit = (await state.get_value('sorted_exp_list'))[num-1]
    else:
        await message.answer(text='Нет такого номера')
        return
    return exp_to_edit
