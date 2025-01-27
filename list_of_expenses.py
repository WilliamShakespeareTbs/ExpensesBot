from aiogram import Router
from aiogram.types import Message
from aiogram.types.callback_query import CallbackQuery

import lists_messages_constructor as lmc
from states import Categories

router = Router()


@router.callback_query(Categories.category_for_look)
async def show_list_of_cat_expences(callback: CallbackQuery):
   await callback.answer('Категория выбрана!')
   try:
      cat_id = int(callback.data.split('_')[-1])
   except ValueError:
      return   
   cur_page = 1
   exp_text, pages_kb = await lmc.message_constructor(cur_page, show_cat=False, cat_id=cat_id, tg_id=callback.message.chat.id)
   await callback.message.answer(text=exp_text, reply_markup=pages_kb)


async def show_list_of_all_expenses(message: Message):
   cur_page = 1
   exp_text, pages_kb = await lmc.message_constructor(cur_page, show_cat=True, cat_id=None, tg_id=message.chat.id)
   await message.answer(text=exp_text, reply_markup=pages_kb)
