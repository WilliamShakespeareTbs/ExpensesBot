from aiogram.filters.callback_data import CallbackData


class PageButton(CallbackData, prefix = 'pb'):
    page: int
    show_cat: bool
    cat_id: int | None
    