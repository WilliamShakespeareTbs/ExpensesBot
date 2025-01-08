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
from validation import date_validation

bot = None
router = Router()


@router.callback_query(Expenses.edit_exp)
async def choose_way_to_show_exp(callback :CallbackQuery, state: FSMContext):
    if callback.data == 'category':
        cat_dict = await request.get_categories(callback.from_user.id)
        cat_buttons = await kb.create_cat_kb(cat_dict)
        await bot.send_message(chat_id = callback.from_user.id, text = 'Выберите категорию расходов', reply_markup = cat_buttons)
        await state.set_state(Expenses.edit_exp_by_cat)
    elif callback.data == 'overall':
        sorted_exp_list = await loe.show_list_of_all_expenses(tg_id=callback.from_user.id, return_list=True)
        await bot.send_message(chat_id = callback.from_user.id, text = 'Введите номер расхода, который хотите редактировать:')
        await state.update_data(sorted_exp_list = sorted_exp_list)


@router.callback_query(Expenses.edit_exp_by_cat)
async def edit_exp_from_cat(callback :CallbackQuery, state: FSMContext):
    cat_id = int(callback.data.split('_')[-1])
    cat_name = await request.get_category_name_from_category_id(cat_id)
    exp_list = await request.get_list_of_expenses_from_category_id(cat_id)
    sorted_exp_list = expenses_sort.sort_expenses_by_date(exp_list)
    head_text = f"Категория: {cat_name}, дата, сумма, комментарий\n"
    exp_text = await cal.create_a_list_on_conditions(sorted_exp_list, head_text, show_cat=False)
    await bot.send_message(chat_id = callback.from_user.id, text = exp_text)
    await bot.send_message(chat_id = callback.from_user.id, text = 'Введите номер расхода, который хотите редактировать:')
    await state.set_state(Expenses.edit_exp)
    await state.update_data(sorted_exp_list = sorted_exp_list)


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
    exp_text = await cal.create_a_list_on_conditions([exp_to_edit], head_text='')
    await state.set_state(Expenses.prop_to_edit)
    await message.answer(text=f"Для редактирования выбран следующий расход:\n{exp_text}\nВыберите, что отредактировать",
                         reply_markup=kb.prop_to_edit_in_expense)
    

@router.callback_query(Expenses.prop_to_edit)
async def edit_exp_from_cat(callback :CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    if callback.data == 'category':
        await state.set_state(Expenses.edit_cat)
        cat_dict = await request.get_categories(callback.from_user.id)
        inline_list = await kb.create_cat_kb(cat_dict)
        await bot.send_message(chat_id = user_id, text = "Выберите категорию, куда переместить расход",
                        reply_markup = inline_list)
    elif callback.data == 'date':
        await state.set_state(Expenses.edit_date)
        await bot.send_message(chat_id = user_id, text = "Введите новую дату в формате ДД.ММ.ГГГГ")
    elif callback.data == 'sum':
        await state.set_state(Expenses.edit_sum)
        await bot.send_message(chat_id = user_id, text = "Введите новую сумму")
    elif callback.data == 'comment':
        await state.set_state(Expenses.edit_comment)
        await bot.send_message(chat_id = user_id, text = "Введите новый комментарий или нажмите пропустить, чтобы оставить расход без комментария",
                         reply_markup = kb.skip_button)
    else: return


@router.callback_query(Expenses.edit_cat)
async def edit_exp_cat(callback: CallbackQuery, state: FSMContext):
    old_cat_id = (await state.get_value('exp_to_edit')).category
    new_cat_id = int(callback.data.split('_')[-1])
    cat_name = await request.get_category_name_from_category_id(old_cat_id)
    await request.transfer_expense_to_another_cat(old_cat_id, new_cat_id)
    await bot.send_message(chat_id = callback.from_user.id, text = f"Перемещение в категорию {cat_name} выполнено успешно")
    await state.clear()


@router.message(Expenses.edit_date, F.text)
async def edit_exp_date(message: Message, state: FSMContext):
    valid_data = date_validation.date_validate(message.text)
    if valid_data:
        norm_data = date_validation.normalize_date(valid_data)
        exp_to_edit = await state.get_value('exp_to_edit')
        await request.change_exp_prop(exp_to_edit, 'date', valid_data)
        await message.answer(text=f"Дата расхода изменена на {norm_data}")
        await state.clear()
        return
    await message.answer(text="Дата не распознана. Пожалуйста, напишите дату в формате ДД.ММ.ГГГГ")


@router.message(Expenses.edit_date)
async def edit_exp_date_nontext(message: Message):
    await message.answer(text="Дата не распознана. Пожалуйста, напишите дату в формате ДД.ММ.ГГГГ")


@router.message(Expenses.edit_sum, F.text)
async def edit_exp_sum(message: Message, state: FSMContext):
    exp_sum = message.text
    if ',' in exp_sum:
        exp_sum = exp_sum.replace(',', '.')
    try:
        converted_sum = float(exp_sum)
    except:
        await message.answer(text="Сообщение не распознано как число. Пожалуйста, введите только цифры с точкой или запятой")
        return
    await request.change_exp_prop(await state.get_value('exp_to_edit'), 'sum', converted_sum)
    await state.clear()
    await message.answer(text=f"Сумма отредактирована на {converted_sum}")


@router.message(Expenses.edit_sum)
async def edit_exp_sum_nontext(message: Message):
    await message.answer(text="Сообщение не распознано как число. Пожалуйста, введите только цифры с точкой или запятой")


@router.callback_query(Expenses.edit_comment)
async def edit_exp_comment_skip(callback: CallbackQuery, state: FSMContext):
    await request.change_exp_prop(await state.get_value('exp_to_edit'), 'comment', None)
    await bot.send_message(chat_id = callback.from_user.id, text = "Изменения внесены, комментарий удалён")
    await state.clear()


@router.message(Expenses.edit_comment, F.text)
async def edit_exp_comment_nontext(message: Message, state: FSMContext):
    await request.change_exp_prop(await state.get_value('exp_to_edit'), 'comment', message.text)
    await message.answer(text="Новый комментарий добавлен")
    await state.clear()


@router.message(Expenses.edit_comment)
async def edit_exp_comment_nontext(message: Message):
    await message.answer(text="Сообщение не распознано как текст, пожалуйста, попробуйте ещё раз")