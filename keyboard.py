from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


async def create_cat_kb(cat_dict):
    categories_kb = InlineKeyboardBuilder()
    for k, v in cat_dict.items():
        categories_kb.add(InlineKeyboardButton(text=v, callback_data=f'cat_{k}'))
    return categories_kb.adjust(2).as_markup()


date_buttons = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Позавчера', callback_data='preyesterday'), InlineKeyboardButton(text='Вчера', callback_data='yesterday')],
    [InlineKeyboardButton(text='Сегодня', callback_data='today'), InlineKeyboardButton(text='Другая дата', callback_data='otherdate')]
])


skip_button = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Пропустить', callback_data='skip')]])


cat_or_overall_show_button = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Выбрать категорию', callback_data='category')],
    [InlineKeyboardButton(text='Показать все расходы', callback_data='overall')]
])


prop_to_edit_in_expense = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Категория', callback_data='category'), InlineKeyboardButton(text='Дата', callback_data='date')],
    [InlineKeyboardButton(text='Сумма', callback_data='sum'), InlineKeyboardButton(text='Комментарий', callback_data='comment')]
])