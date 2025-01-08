from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup


class Categories(StatesGroup):
    category_name = State()
    category_for_expense = State()
    category_for_look = State()
    delete_cat = State()
    edit_cat = State()


class Expenses(StatesGroup):
    date = State()
    sum = State()
    comment = State()
    delete_exp = State()
    delete_exp_by_cat = State()
    edit_exp = State()
    edit_exp_by_cat = State()
    prop_to_edit = State()
    edit_cat = State()
    edit_date = State()
    edit_sum = State()
    edit_comment = State()