from validation import date_validation
import request

async def create_a_list_on_conditions(sorted_exp_list, head_text: str, show_cat = True):
    sorted_exp_list = sorted_exp_list
    exp_text = head_text
    sequence_of_parameters = []
    itt = 1
    for elem in sorted_exp_list:
        itt_list = []
        itt_list.append(str(itt) + '. ')
        if(show_cat):
            itt_list.append(await request.get_category_name_from_category_id(elem.category) + ', ')
        itt_list.append(date_validation.normalize_date(elem.date) + ', ')
        itt_list.append(elem.sum)
        if(elem.comment):
            itt_list.append(', ' + elem.comment)
        sequence_of_parameters.append(itt_list)
        itt+=1
    for elem in sequence_of_parameters:
        for sub_elem in elem:
            exp_text = exp_text + f'{sub_elem}'
        exp_text = exp_text + '\n'
    return exp_text

