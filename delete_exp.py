from aiogram import Router, F
from aiogram.types import Message
from aiogram.types.callback_query import CallbackQuery
from aiogram.fsm.context import FSMContext

from states import Expenses
import expenses_sort
import keyboard as kb
import list_of_expenses as loe
import request
import create_a_list_of_expenses as cal

bot = None
router = Router()


@router.callback_query(Expenses.delete_exp)
async def choose_way_to_show_exp(callback :CallbackQuery, state: FSMContext):
    if callback.data == 'category':
        cat_dict = await request.get_categories(callback.from_user.id)
        cat_buttons = await kb.create_cat_kb(cat_dict)
        await bot.send_message(chat_id = callback.from_user.id, text = 'Выберите категорию расходов', reply_markup = cat_buttons)
        await state.set_state(Expenses.delete_exp_by_cat)
    elif callback.data == 'overall':
        sorted_exp_list = await loe.show_list_of_all_expenses(tg_id=callback.from_user.id, return_list=True)
        await bot.send_message(chat_id = callback.from_user.id, text = 'Введите номер расхода, который хотите удалить:')
        await state.update_data(sorted_exp_list = sorted_exp_list)


@router.callback_query(Expenses.delete_exp_by_cat)
async def delete_exp_from_cat(callback :CallbackQuery, state: FSMContext):
    cat_id = int(callback.data.split('_')[-1])
    cat_name = await request.get_category_name_from_category_id(cat_id)
    exp_list = await request.get_list_of_expenses_from_category_id(cat_id)
    sorted_exp_list = expenses_sort.sort_expenses_by_date(exp_list)
    head_text = f"Категория: {cat_name}, дата, сумма, комментарий\n"
    exp_text = await cal.create_a_list_on_conditions(sorted_exp_list, head_text, show_cat=False)
    await bot.send_message(chat_id = callback.from_user.id, text = exp_text)
    await bot.send_message(chat_id = callback.from_user.id, text = 'Введите номер расхода, который хотите удалить:')
    await state.set_state(Expenses.delete_exp)
    await state.update_data(sorted_exp_list = sorted_exp_list)


@router.message(Expenses.delete_exp, F.text)
async def delete_by_num(message: Message, state: FSMContext):
    try:
        num = int(message.text)
    except:
        await message.answer(text='Это не число, попробуйте снова!')
        return
    if num > 0 and num <= len(await state.get_value('sorted_exp_list')):
        exp_to_delete = (await state.get_value('sorted_exp_list'))[num-1]
    else:
        return
    exp_text = await cal.create_a_list_on_conditions([exp_to_delete], head_text='')
    await request.delete_expence_by_exp_class(exp_to_delete)
    await state.clear()
    await message.answer(text=f"Удалён следующий расход:\n{exp_text}")
    