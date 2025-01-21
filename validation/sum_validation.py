from aiogram.types import Message

def validate_sum(message: Message):
    try:
        exp_sum = message.text
        if ',' in exp_sum:
            exp_sum = exp_sum.replace(',', '.')
        converted_sum = float(exp_sum)
        sum = round(converted_sum, 2)
    except:
        return None
    return {'sum' : sum}