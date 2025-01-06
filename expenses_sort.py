from datetime import datetime
from validation import date_validation

def sort_expenses_by_date(list_of_expenses: list):
    sorted_list = []
    for elem in list_of_expenses:
        index = -1
        for i in sorted_list:
            if convert_date_to_num(i.date) > convert_date_to_num(elem.date):
                index = sorted_list.index(i)
                break
        if index == -1:
            sorted_list.append(elem)
        else: sorted_list.insert(index, elem)
    return sorted_list


def convert_date_to_num(date_from_list: datetime):
    date_as_num = int(date_validation.flip_date(date_from_list))
    return date_as_num