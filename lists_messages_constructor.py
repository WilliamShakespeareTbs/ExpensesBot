import math

from validation import date_validation
import request
import keyboard as kb

async def create_a_list_from_objects(exp_list, show_cat = True):
    sequence_of_parameters = []
    itt = 1
    if len(exp_list) < 1:
        return "Расходы отсутствуют"
    for elem in exp_list:
        itt_list = []
        itt_list.append(str(itt) + '. ')
        itt+=1
        if(show_cat):
            itt_list.append(await request.get_category_name_from_category_id(elem.category) + ', ')
        itt_list.append(date_validation.normalize_date(elem.date) + ', ')
        itt_list.append(elem.sum)
        if(elem.comment):
            itt_list.append(', ' + elem.comment)
        itt_list.append('\n')
        sequence_of_parameters.append(itt_list)
    return sequence_of_parameters


async def message_constructor(page, show_cat, cat_id: int | None, tg_id: int | None):
    if(cat_id):
        cat_name = await request.get_category_name_from_category_id(cat_id)
        exp_list = await request.get_list_of_expenses_from_category_id(cat_id)
    else:
        cat_name = None
        exp_list = await request.get_list_of_all_expenses_in_one_query(tg_id)
    sequence_list = await create_a_list_from_objects(exp_list, show_cat)
    if type(sequence_list) is not list:
        return sequence_list, None
    if(show_cat):
        head_text = f"Категория, дата, сумма, комментарий\n"
    else:
        head_text = f"Категория: {cat_name}, дата, сумма, комментарий\n"
    exp_text = head_text
    exp_per_page = 20
    num_of_pages = math.ceil(len(sequence_list)/5)
    prev = True
    next = True
    last_index = -(page-1)*exp_per_page
    first_index = -(page)*exp_per_page
    if page == num_of_pages:
        first_index = 0
        prev = False
    cut_list = sequence_list[first_index:last_index]
    if page == 1:
        cut_list = sequence_list[first_index:]
        next = False
    pages_kb = await kb.button_to_list_pages(prev, next, page, show_cat, cat_id)
    if len(sequence_list) <= exp_per_page:
        cut_list = sequence_list
    for el in cut_list:
        for sub_el in el:
            exp_text = exp_text + f'{sub_el}'
    return exp_text, pages_kb    


async def simple_message_constructor(exp_list):
    short_seq = await create_a_list_from_objects(exp_list, show_cat=True)
    exp_text = ''
    for el in short_seq:
        for sub_el in el:
            exp_text = exp_text + f'{sub_el}'
    return exp_text
