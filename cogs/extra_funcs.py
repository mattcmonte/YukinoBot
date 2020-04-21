# Some extra misc functions.

import datetime
import json
import random


def duplicate_count(polls, poll_name):
    """Returns number of duplicate poll names in a list of dictionaries.
    
    Keyword Arguments:
    polls     -- a list of dictionaries
    poll_name -- the poll name to check for duplicates of
    """
    counter = 0
    for poll_dict in polls:
        if poll_dict['name'] == poll_name.content:
            counter += 1
    return counter

def dump_poll_data(polls):
    """Writes poll data from a list of dictionaries to a json file.
    
    Keyword Arguments:
    polls -- a list of dictionaries
    """
    with open('./cogs/polls.json', 'w', encoding='utf-8') as poll_file:
        json.dump(polls, poll_file, indent=2)

def load_poll_data():
    """Reads poll data from a json file into a list of dictionaries."""
    polls = []
    
    with open('./cogs/polls.json', 'r', encoding='utf-8') as poll_file:
        try:
            polls = json.load(poll_file)
        except json.JSONDecodeError:
            pass
    return polls

def generate_hex_int():
    """Returns a randomly generated hexadecimal integer."""
    random_num = random.randint(0, 16777215)
    hex_num = hex(random_num)
    return int(hex_num, 16)

def get_next_index(polls):
    """Returns the next index for a list of dictionaries.

    Keyword Arguments:
    polls -- a list of dictionaries
    """
    new_index = ''
    if polls == []:
        new_index = 1
    else:
        indexes = [
            dictionary['index'] for dictionary in polls
        ]
        new_index = max(indexes) + 1
    return new_index

def format_date(date_dict):
    """Returns a date formatted in mm-dd-yyyy.

    Keyword Arguments:
    date_dict -- dict containing date information
    """
    formatted_date = 'n/a'
    if date_dict['month'] != None:
        str_date = (f'{date_dict["month"]}/{date_dict["day"]}/'
                    f'{date_dict["year"]}')

        date_obj = datetime.datetime.strptime(str_date, '%m/%d/%Y')
        formatted_date = date_obj.strftime('%A %b %d, %Y')
    return formatted_date

def list_to_str(genres):
    """Returns a string containing each list element seperated by a comma.

    Keyword Arguments:
    genres -- the list to be formatted
    """
    genres = ', '.join(genre for genre in genres)
    return genres

def remove_whitespace(the_list):
    """Returns a list of strings with each element's whitespace removed.

    Keyword Arguments:
    the_list -- a list of strings
    """
    return [item.strip() for item in the_list]