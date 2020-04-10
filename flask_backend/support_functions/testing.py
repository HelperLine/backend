
from flask_backend import call_queue
from flask_backend.database_scripts.call_scripts import dequeue

from datetime import datetime


def call_records_to_list(records):
    # in: [{'call_id': 'A'}, {'call_id': 'B'}]
    # out: ['A', 'B']
    return [record['call_id'] for record in records]


def lists_match(list_1, list_2):
    # duplicate check
    new_list_1 = []
    new_list_2 = []

    # equality check
    for element_1 in list_1:
        if element_1 not in new_list_1:
            new_list_1.append(element_1)

        if element_1 not in list_2:
            return False

    for element_2 in list_2:
        if element_2 not in new_list_2:
            new_list_2.append(element_2)

        if element_2 not in list_1:
            return False

    return (len(list_1) == len(new_list_1)) and (len(list_2) == len(new_list_2))


def check_queues(test_no, desired_local_list, desired_global_list, desired_urgent_list):
    current_timestamp = datetime.now()

    local_calls = list(call_queue.find(
        {'local': True},
        {'_id': 0, 'call_id': 1}))

    global_calls = list(call_queue.find(
        {'local': True, 'timestamp_received': {'$lt': current_timestamp - dequeue.local_timeout_timedelta}},
        {'_id': 0, 'call_id': 1}))
    global_calls += list(call_queue.find(
        {'local': False},
        {'_id': 0, 'call_id': 1}))

    urgent_calls = list(call_queue.find(
        {'timestamp_received': {'$lt': current_timestamp - dequeue.global_timeout_timedelta}},
        {'_id': 0, 'call_id': 1}))


    result_1 = {
        'name': f'Test {test_no} (local queue)',
        'result': lists_match(desired_local_list, call_records_to_list(local_calls)),
    }
    if not result_1['result']:
        result_1.update({'details': f'{call_records_to_list(local_calls)} != {desired_local_list}'})

    result_2 = {
        'name': f'Test {test_no} (global queue)',
        'result': lists_match(desired_global_list, call_records_to_list(global_calls)),
    }
    if not result_2['result']:
        result_2.update({'details': f'{call_records_to_list(global_calls)} != {desired_global_list}'})

    result_3 = {
        'name': f'Test {test_no} (urgent queue)',
        'result': lists_match(desired_urgent_list, call_records_to_list(urgent_calls)),
    }
    if not result_3['result']:
        result_3.update({'details': f'{call_records_to_list(urgent_calls)} != {desired_urgent_list}'})

    return [result_1, result_2, result_3]
