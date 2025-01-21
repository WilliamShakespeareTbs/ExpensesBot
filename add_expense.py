from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.types.callback_query import CallbackQuery
import datetime

import request
import keyboard as kb
from states import Categories, Expenses
from validation import date_validation, sum_validation

router = Router()


async def switch_from_date_to_sum(valid_date, state, message):
    await state.update_data(date=valid_date)
    await state.set_state(Expenses.sum)
    norm_date = date_validation.normalize_date(valid_date)
    await message.answer(text=f"Дата внесена: {norm_date}. Пожалуйста, введите сумму расхода:")


@router.callback_query(Categories.category_for_expense)
async def choose_list_of_expences(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Expenses.date)
    await state.update_data(cat_id = int(callback.data.split('_')[-1]))
    await callback.message.answer(text='Выберите дату расходов:', reply_markup=kb.date_buttons)


@router.message(Expenses.date, date_validation.date_validate)
async def enter_custom_date(message: Message, state: FSMContext, valid_date: datetime):
    await switch_from_date_to_sum(valid_date, state, message)


@router.message(Expenses.date)
async def enter_nontext_date(message: Message):
    await message.answer(text="Дата не распознана. Пожалуйста, напишите дату в формате ДД.ММ.ГГГГ")


@router.callback_query(Expenses.date)
async def choose_date_of_expences(callback: CallbackQuery, state: FSMContext):
    delta_day = 0
    if callback.data == 'otherdate':
        await callback.message.answer(text = 'Напишите дату в формате ДД.ММ.ГГГГ')
        return
    elif callback.data == 'today':
        delta_day = 0
    elif callback.data == 'yesterday':
        delta_day = 1
    elif callback.data == 'preyesterday':
        delta_day = 2
    valid_date = datetime.datetime.now().date() - datetime.timedelta(days=delta_day)
    await switch_from_date_to_sum(valid_date, state, callback.message)


@router.message(Expenses.sum, sum_validation.validate_sum )
async def sum_of_expense(message: Message, state: FSMContext, sum: float):
    await state.update_data(sum = sum)
    await state.set_state(Expenses.comment)
    await message.answer(text="При желании добавьте комментарий (ограничение 100 символов), либо нажмите 'Пропустить'", reply_markup=kb.skip_button)


@router.message(Expenses.sum, F.text)
async def not_sum(message: Message):
    await message.answer(text="Сообщение не распознано как число. Пожалуйста, введите только цифры с точкой или запятой")


@router.message(Expenses.sum)
async def wrong_sum(message: Message):
    await message.answer(text="Сообщение не распознано. Пожалуйста, введите сумму расхода")


@router.message(Expenses.comment, F.text)
async def exp_comment(message: Message, state: FSMContext):
    exp_com = message.text
    if len(exp_com) > 100:
        exp_com = exp_com[:100]
    data = await state.update_data(comment = exp_com)
    await request.add_expension(data)
    await state.clear()
    category_name = await request.get_category_name_from_category_id(data['cat_id'])
    norm_date = date_validation.normalize_date(data['date'])
    await message.answer(text=f"Расход успешно внесён!\nКатегория: {category_name}\nДата: {norm_date}\nСумма: {data['sum']}\nКомментарий: {data['comment']}")


@router.message(Expenses.comment)
async def exp_comment_nontext(message: Message):
    await message.answer(text="Сообщение не распознано как текст, попробуйте ещё раз")
    

@router.callback_query(Expenses.comment)
async def skip_comment(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await request.add_expension(data)
    await state.clear()
    category_name = await request.get_category_name_from_category_id(data['cat_id'])
    norm_date = date_validation.normalize_date(data['date'])
    await callback.message.answer(text = f"Расход успешно внесён!\nКатегория: {category_name}\nДата: {norm_date}\nСумма: {data['sum']}")
    