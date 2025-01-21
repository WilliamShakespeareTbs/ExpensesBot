from datetime import datetime
from aiogram.types import Message

def date_validate(message: Message):
    try:
        date_pieces = message.text.split('.')
        if(len(date_pieces) == 3):
            day = int(date_pieces[0])
            month = int(date_pieces[1])
            year = int(date_pieces[2])
            valid_date = datetime(year, month, day)
            return {'valid_date' : valid_date}
    except:
        pass
    return None


def normalize_date(date: datetime) -> str:
    if date.day > 9:
        norm_day = str(date.day)
    else: norm_day = '0' + str(date.day)
    if date.month > 9:
        norm_month = str(date.month)
    else: norm_month = '0' + str(date.month)
    norm_date = f'{norm_day}.{norm_month}.{date.year}'
    return norm_date


def flip_date(date: datetime):
    if date.day > 9:
        flipped_day = str(date.day)
    else: flipped_day = '0' + str(date.day)
    if date.month > 9:
        flipped_month = str(date.month)
    else: flipped_month = '0' + str(date.month)
    flipped_date = f'{date.year}{flipped_month}{flipped_day}'
    return flipped_date