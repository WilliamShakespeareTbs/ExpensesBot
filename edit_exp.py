from datetime import datetime
from aiogram import Router, F
from aiogram.types import Message
from aiogram.types.callback_query import CallbackQuery
from aiogram.fsm.context import FSMContext

from states import Expenses
import keyboard as kb
import list_of_expenses as loe
import request
import create_a_list_of_expenses as cal
from validation import date_validation, sum_validation

router = Router()


@router.callback_query(Expenses.edit_exp)
async def choose_way_to_show_exp(callback :CallbackQuery, state: FSMContext):
    if callback.data == 'category':
        cat_dict = await request.get_categories(callback.from_user.id)
        cat_buttons = await kb.create_cat_kb(cat_dict)
        await callback.message.answer(text = 'Выберите категорию расходов', reply_markup = cat_buttons)
        await state.set_state(Expenses.edit_exp_by_cat)
    elif callback.data == 'overall':
        exp_list = await request.get_list_of_all_expenses_in_one_query(callback.message.chat.id)
        exp_text, pages_kb = await cal.message_constructor(page=1, show_cat=True, cat_id=None, tg_id=callback.message.chat.id)
        await callback.message.answer(text = exp_text, reply_markup=pages_kb)
        await callback.message.answer(text = 'Введите номер расхода, который хотите редактировать:')
        await state.update_data(sorted_exp_list = exp_list)


@router.callback_query(Expenses.edit_exp_by_cat)
async def edit_exp_from_cat(callback :CallbackQuery, state: FSMContext):
    cat_id = int(callback.data.split('_')[-1])
    exp_list = await request.get_list_of_expenses_from_category_id(cat_id)
    if exp_list:
        exp_text, pages_kb = await cal.message_constructor(page=1, show_cat=False, cat_id=cat_id, tg_id=callback.message.chat.id)
    else:
        exp_text = await cal.message_constructor(page=1, show_cat=False, cat_id=cat_id, tg_id=callback.message.chat.id)
        pages_kb = None
  #  exp_list = await request.get_list_of_all_expenses_in_one_query(callback.message.chat.id)
    
    await callback.message.answer(text = exp_text, reply_markup=pages_kb)
    if pages_kb:
        await callback.message.answer(text = 'Введите номер расхода, который хотите редактировать:')
    await state.set_state(Expenses.edit_exp)
    await state.update_data(sorted_exp_list = exp_list)


@router.message(Expenses.edit_exp, F.text)
async def edit_by_num(message: Message, state: FSMContext):
    try:
        num = int(message.text)
    except:
        await message.answer(text='Это не число, попробуйте снова!')
        return
    if num > 0 and num <= len(await state.get_value('sorted_exp_list')):
        exp_to_edit = (await state.get_value('sorted_exp_list'))[num-1]
        await state.update_data(exp_to_edit = exp_to_edit)
    else:
        await message.answer(text='Нет такого номера')
        return
    exp_text = await cal.simple_message_constructor([exp_to_edit])
    await state.set_state(Expenses.prop_to_edit)
    await message.answer(text=f"Для редактирования выбран следующий расход:\n{exp_text}\nВыберите, что отредактировать",
                         reply_markup=kb.prop_to_edit_in_expense)
    

@router.callback_query(Expenses.prop_to_edit)
async def edit_exp_from_cat(callback :CallbackQuery, state: FSMContext):
    if callback.data == 'category':
        await state.set_state(Expenses.edit_cat)
        cat_dict = await request.get_categories(callback.from_user.id)
        inline_list = await kb.create_cat_kb(cat_dict)
        await callback.message.answer(text = "Выберите категорию, куда переместить расход",
                        reply_markup = inline_list)
    elif callback.data == 'date':
        await state.set_state(Expenses.edit_date)
        await callback.message.answer(text = "Введите новую дату в формате ДД.ММ.ГГГГ")
    elif callback.data == 'sum':
        await state.set_state(Expenses.edit_sum)
        await callback.message.answer(text = "Введите новую сумму")
    elif callback.data == 'comment':
        await state.set_state(Expenses.edit_comment)
        await callback.message.answer(text = "Введите новый комментарий или нажмите пропустить, чтобы оставить расход без комментария",
                         reply_markup = kb.skip_button)
    else: return


@router.callback_query(Expenses.edit_cat)
async def edit_exp_cat(callback: CallbackQuery, state: FSMContext):
    exp_to_edit = await state.get_value('exp_to_edit')
    new_cat_id = int(callback.data.split('_')[-1])
    old_cat_name = await request.get_category_name_from_category_id(exp_to_edit.category)
    new_cat_name = await request.get_category_name_from_category_id(new_cat_id)
    await request.transfer_expense_to_another_cat(exp_to_edit, new_cat_id)
    await callback.message.answer(text = f"Перемещение из категории {old_cat_name} в категорию {new_cat_name} выполнено успешно")
    await state.clear()


@router.message(Expenses.edit_date, date_validation.date_validate)
async def edit_exp_date(message: Message, state: FSMContext, valid_date: datetime):
    norm_data = date_validation.normalize_date(valid_date)
    exp_to_edit = await state.get_value('exp_to_edit')
    await request.change_exp_prop(exp_to_edit, 'date', valid_date)
    await message.answer(text=f"Дата расхода изменена на {norm_data}")
    await state.clear()


@router.message(Expenses.edit_date)
async def edit_exp_date_nontext(message: Message):
    await message.answer(text="Дата не распознана. Пожалуйста, напишите дату в формате ДД.ММ.ГГГГ")


@router.message(Expenses.edit_sum, sum_validation.validate_sum)
async def edit_exp_sum(message: Message, state: FSMContext, sum: float):
    await request.change_exp_prop(await state.get_value('exp_to_edit'), 'sum', sum)
    await state.clear()
    await message.answer(text=f"Сумма отредактирована на {sum}")


@router.message(Expenses.edit_sum)
async def edit_exp_sum_nontext(message: Message):
    await message.answer(text="Сообщение не распознано как число. Пожалуйста, введите только цифры с точкой или запятой")


@router.callback_query(Expenses.edit_comment)
async def edit_exp_comment_skip(callback: CallbackQuery, state: FSMContext):
    await request.change_exp_prop(await state.get_value('exp_to_edit'), 'comment', None)
    await callback.message.answer(text = "Изменения внесены, комментарий удалён")
    await state.clear()


@router.message(Expenses.edit_comment, F.text)
async def edit_exp_comment_nontext(message: Message, state: FSMContext):
    exp_com = message.text
    if len(exp_com) > 100:
        exp_com = exp_com[:100]
    await request.change_exp_prop(await state.get_value('exp_to_edit'), 'comment', exp_com)
    await message.answer(text="Новый комментарий добавлен")
    await state.clear()


@router.message(Expenses.edit_comment)
async def edit_exp_comment_nontext(message: Message):
    await message.answer(text="Сообщение не распознано как текст, пожалуйста, попробуйте ещё раз")