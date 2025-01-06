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