# Some extra misc functions.

import datetime
import json
import random


def duplicate_count(polls, poll_name):
    """Returns number of duplicate poll names in a list of dictionaries."""
    counter = 0
    for poll_dict in polls:
        if poll_dict['name'] == poll_name.content:
        # or polls.index(poll_dict['name']) == poll_name.content:
            counter += 1

    # dup_count = [
    #     obj['name'].count(poll_name.content) for obj in polls
    # ]
    # print(dup_count)
    # if dup_count == []:
    #     dup_count.append(0)
    # print(dup_count)
    return counter


def dump_poll_data(polls):
    """Writes poll data from a list of dictionaries to a json file."""
    with open('./cogs/polls.json', 'w', encoding='utf-8') as poll_file:
        json.dump(polls, poll_file, indent=2)


def load_poll_data():
    """Reads poll data from a json file into a list of dictionaries."""
    polls = []
    with open('./cogs/polls.json', 'r', encoding='utf-8') as poll_file:
        polls = json.load(poll_file)
    return polls

def generate_hex_int():
    """Returns a randomly generated hexadecimal integer."""
    random_num = random.randint(0, 16777215)
    hex_num = hex(random_num)
    return int(hex_num, 16)

def get_next_index(dict_list):
    """Returns the next index for a list of dictionaries.

    Keyword Arguments:
    dict_list -- a list of dictionaries
    """
    new_index = ""
    try:
        indexes = [
            dictionary['index'] for dictionary in dict_list
        ]
        print(indexes)
        new_index = max(indexes) + 1
    except KeyError:
        new_index = 1
    except ValueError:
        pass
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