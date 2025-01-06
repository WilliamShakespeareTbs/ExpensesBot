from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram import Router, Bot, F
from aiogram.filters import callback_data
from aiogram.types.callback_query import CallbackQuery
from aiogram.types import Message

import expenses_sort
import request
from states import Categories, Expenses
from validation import date_validation

router = Router()
bot = None


@router.callback_query(Categories.category_for_look)
async def show_list_of_cat_expences(callback: CallbackQuery, state: FSMContext):
   cat_id = int(callback.data.split('_')[-1])
   cat_name = await request.get_category_name_from_category_id(cat_id)
   exp_list = await request.get_list_of_expenses_from_category_id(cat_id)
   head_text = f"Категория: {cat_name}, дата, сумма, комментарий\n"
   exp_text = await sort_list_and_make_message(head_text, exp_list)
   await bot.send_message(chat_id = callback.from_user.id, text = exp_text)
   await state.clear()


async def show_list_of_all_expenses(tg_id, state):
   exp_list = await request.get_list_of_all_expenses(tg_id)
   head_text = f"Категория, дата, сумма, комментарий\n"
   exp_text = await sort_list_and_make_message(head_text, exp_list, show_cat_name=True)
   await bot.send_message(chat_id = tg_id, text = exp_text)
   await state.clear()



async def sort_list_and_make_message(head_text, exp_list, show_cat_name = False):
   sorted_exp_list = expenses_sort.sort_expenses_by_date(exp_list)
   exp_text = head_text
   itt = 1
   for el in sorted_exp_list:
      el_date = date_validation.normalize_date(el.date)
      if show_cat_name:
         el_cat = await request.get_category_name_from_category_id(el.category)
         if(el.comment):
            exp_text = exp_text + f"{itt}. {el_cat}, {el_date}, {el.sum}, {el.comment}\n"
         else: exp_text = exp_text + f"{itt}. {el_cat}, {el_date}, {el.sum}\n"
      else:
         if(el.comment):
            exp_text = exp_text + f"{itt}. {el_date}, {el.sum}, {el.comment}\n"
         else: exp_text = exp_text + f"{itt}. {el_date}, {el.sum}\n"
      itt+=1
   return exp_text