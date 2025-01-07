from aiogram.fsm.context import FSMContext
from aiogram import Router
from aiogram.types.callback_query import CallbackQuery

import create_a_list_of_expenses as cal
import request
import expenses_sort
from states import Categories

router = Router()
bot = None


@router.callback_query(Categories.category_for_look)
async def show_list_of_cat_expences(callback: CallbackQuery, state: FSMContext):
   cat_id = int(callback.data.split('_')[-1])
   cat_name = await request.get_category_name_from_category_id(cat_id)
   exp_list = await request.get_list_of_expenses_from_category_id(cat_id)
   sorted_exp_list = expenses_sort.sort_expenses_by_date(exp_list)
   head_text = f"Категория: {cat_name}, дата, сумма, комментарий\n"
   exp_text = await cal.create_a_list_on_conditions(sorted_exp_list, head_text, show_cat=False)
   await bot.send_message(chat_id = callback.from_user.id, text = exp_text)
   await state.clear()


async def show_list_of_all_expenses(tg_id, return_list = False):
   exp_list = await request.get_list_of_all_expenses(tg_id)
   sorted_exp_list = expenses_sort.sort_expenses_by_date(exp_list)
   head_text = f"Категория, дата, сумма, комментарий\n"
   exp_text = await cal.create_a_list_on_conditions(sorted_exp_list, head_text)
   await bot.send_message(chat_id = tg_id, text = exp_text)
   if(return_list):
      return sorted_exp_list

