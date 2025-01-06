from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.types.callback_query import CallbackQuery
import datetime

import request
import keyboard as kb
from states import Categories, Expenses
from validation import date_validation

router = Router()
bot = None


async def switch_from_date_to_sum(valid_data, state, chat_id):
    await state.update_data(date=valid_data)
    await state.set_state(Expenses.sum)
    norm_date = date_validation.normalize_date(valid_data)
    await bot.send_message(chat_id=chat_id, text=f"Дата внесена: {norm_date}. Пожалуйста, введите сумму расхода:")


@router.callback_query(Categories.category_for_expense)
async def choose_list_of_expences(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Expenses.date)
    await state.update_data(cat_id = int(callback.data.split('_')[-1]))
    await bot.send_message(chat_id=callback.from_user.id, text='Выберите дату расходов:', reply_markup=kb.date_buttons)


@router.message(Expenses.date, F.text)
async def enter_custom_date(message: Message, state: FSMContext):
    valid_data = date_validation.date_validate(message.text)
    if valid_data:
        await switch_from_date_to_sum(valid_data, state, message.from_user.id)
        return
    await message.answer(text="Дата не распознана. Пожалуйста, напишите дату в формате ДД.ММ.ГГГГ")


@router.callback_query(Expenses.date)
async def choose_date_of_expences(callback: CallbackQuery, state: FSMContext):
    delta_day = 0
    if callback.data == 'otherdate':
        await bot.send_message(chat_id=callback.from_user.id, text = 'Напишите дату в формате ДД.ММ.ГГГГ')
        return
    elif callback.data == 'today':
        delta_day = 0
    elif callback.data == 'yesterday':
        delta_day = 1
    elif callback.data == 'preyesterday':
        delta_day = 2
    valid_data = datetime.datetime.now().date() - datetime.timedelta(days=delta_day)
    await switch_from_date_to_sum(valid_data, state, callback.from_user.id)


@router.message(Expenses.sum, F.text)
async def sum_of_expense(message: Message, state: FSMContext):
    exp_sum = message.text
    if ',' in exp_sum:
        exp_sum = exp_sum.replace(',', '.')
    try:
        converted_sum = float(exp_sum)
    except:
        await message.answer(text="Сообщение не распознано как число. Пожалуйста, введите только цифры с точкой или запятой")
        return
    await state.update_data(sum = round(converted_sum, 2))
    await state.set_state(Expenses.comment)
    await message.answer(text="При желании добавьте комментарий (ограничение 100 символов), либо нажмите 'Пропустить'", reply_markup=kb.skip_button)


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


@router.callback_query(Expenses.comment)
async def skip_comment(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await request.add_expension(data)
    await state.clear()
    category_name = await request.get_category_name_from_category_id(data['cat_id'])
    norm_date = date_validation.normalize_date(data['date'])
    await bot.send_message(chat_id=callback.from_user.id,
        text = f"Расход успешно внесён!\nКатегория: {category_name}\nДата: {norm_date}\nСумма: {data['sum']}")
    