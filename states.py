from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup


class Categories(StatesGroup):
    category_name = State()
    category_for_expense = State()
    category_for_look = State()


class Expenses(StatesGroup):
    date = State()
    sum = State()
    comment = State()