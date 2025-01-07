from aiogram.filters import Command, CommandStart
from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

import request
import keyboard as kb
import list_of_expenses as loe
from states import Categories, Expenses

router = Router()


@router.message(CommandStart())
async def start(message: Message):
    is_new = await request.check_for_user(message.from_user.id)
    if is_new:
        await message.answer('Добро пожаловать! Вам доступна категория Прочее')
        await request.add_new_user(message.from_user.id)
    else:
        await message.answer("База данных уже создана")


@router.message(Command('addcategory'))
async def new_category(message: Message, state: FSMContext):
    await message.answer('Выберите имя для новой категории: ')
    await state.set_state(Categories.category_name)


@router.message(Command('showcategories'))
async def show_categories(message: Message, state: FSMContext):
    await state.set_state(Categories.category_for_look)
    cat_dict = await request.get_categories(message.from_user.id)
    inline_list = await kb.create_cat_kb(cat_dict)
    await message.answer("Вот все категории: ", reply_markup=inline_list)


@router.message(Command('addexpense'))
async def add_new_expense(message: Message, state: FSMContext):
    await state.set_state(Categories.category_for_expense)
    cat_dict = await request.get_categories(message.from_user.id)
    inline_list = await kb.create_cat_kb(cat_dict)
    await message.answer("Выберите категорию расходов: ", reply_markup=inline_list)


@router.message(Command('showexpenses'))
async def show_categories(message: Message, state: FSMContext):
    await loe.show_list_of_all_expenses(message.from_user.id)


@router.message(Command('deleteexpense'))
async def delete_expense(message: Message, state: FSMContext):
    await state.set_state(Expenses.delete_exp)
    await message.answer(text='Выберите расход для удаления: ', reply_markup=kb.cat_or_overall_show_button)


@router.message(Command('deletecategory'))
async def delete_category(message: Message, state: FSMContext):
    await state.set_state(Categories.delete_cat)
    cat_dict = await request.get_categories(message.from_user.id)
    inline_list = await kb.create_cat_kb(cat_dict)
    await message.answer(text="Выберите категорию для удаления, все расходы будут перемещены в Прочее", reply_markup=inline_list)