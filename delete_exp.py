from aiogram import Router, F
from aiogram.types import Message
from aiogram.types.callback_query import CallbackQuery
from aiogram.fsm.context import FSMContext

from states import Expenses
import expenses_manager
import request
import lists_messages_constructor as lmr

router = Router()


@router.callback_query(Expenses.delete_exp)
async def choose_way_to_show_exp(callback :CallbackQuery, state: FSMContext):
    await callback.answer('Способ отображения выбран')
    if callback.data == 'category':
        await expenses_manager.show_by_category(callback, Expenses.delete_exp_by_cat, state)
    elif callback.data == 'overall':
        await expenses_manager.show_all(callback, 'удалить', state)


@router.callback_query(Expenses.delete_exp_by_cat)
async def delete_exp_from_cat(callback :CallbackQuery, state: FSMContext):
    await expenses_manager.choose_num_from_cat(callback, 'удалить', Expenses.delete_exp, state)


@router.message(Expenses.delete_exp, F.text)
async def delete_by_num(message: Message, state: FSMContext):
    exp_to_delete = await expenses_manager.filter_num(message, state)
    if not exp_to_delete: return
    exp_text = await lmr.simple_message_constructor([exp_to_delete])
    await request.delete_expence_by_exp_class(exp_to_delete)
    await state.clear()
    await message.answer(text=f"Удалён следующий расход:\n{exp_text}")
    