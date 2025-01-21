from aiogram import Router
from aiogram.types.callback_query import CallbackQuery

import create_a_list_of_expenses as cal
from callback_constructor import PageButton

router = Router()


@router.callback_query(PageButton.filter())
async def change_page(callback_query: CallbackQuery, callback_data: PageButton):
    new_page = callback_data.page
    exp_text, pages_kb = await cal.message_constructor(new_page, callback_data.show_cat, callback_data.cat_id, callback_query.message.chat.id)
    await callback_query.message.edit_text(text=exp_text, reply_markup=pages_kb)
