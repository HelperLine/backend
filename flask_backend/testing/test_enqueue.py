
from flask_backend import call_queue, calls_collection
from flask_backend.database_scripts.hotline_scripts import enqueue
from flask_backend.support_functions import testing

from datetime import datetime, timedelta
from bson import ObjectId
import time



def test_enqueue():

    results = []

    # Test Start) EMPTY all queues
    calls_collection.delete_many({})
    call_queue.delete_many({})

    call_id_A = calls_collection.insert_one({
        'timestamp_received': datetime.now(),
        'local': True,
        'zip_code': '80000'
    }).inserted_id

    call_id_B = calls_collection.insert_one({
        'timestamp_received': datetime.now(),
        'local': False,
        'zip_code': '80000'
    }).inserted_id

    call_id_C = calls_collection.insert_one({
        'timestamp_received': datetime.now() + timedelta(seconds=5),
        'local': True,
        'zip_code': '80000'
    }).inserted_id

    call_id_D = calls_collection.insert_one({
        'timestamp_received': datetime.now() + timedelta(seconds=5),
        'local': False,
        'zip_code': '80000'
    }).inserted_id


    # T1) Add [local A] and [global B]
    timestamp = datetime.now()
    status_1 = enqueue.enqueue(call_id_A)['status']
    status_2 = enqueue.enqueue(call_id_B)['status']

    results += [
        {'name': 'Test 1 (local add)', 'result': status_1 == 'ok'},
        {'name': 'Test 1 (global add)', 'result': status_2 == 'ok'}
    ]

    # .) CHECK manually if everything is set correctly -> local: [A], global: [B], urgent: []
    results += testing.check_queues(2, [call_id_A], [call_id_B], [])

    # .) Add [local A] and [global B] (both are invalid but non-breaking operations)
    timestamp = datetime.now()
    status_1 = enqueue.enqueue(call_id_A)['status']
    status_2 = enqueue.enqueue(call_id_B)['status']

    results += [
        {'name': 'Test 4 (local duplicate add)', 'result': status_1 == 'call id already exists'},
        {'name': 'Test 4 (global duplicate add)', 'result': status_2 == 'call id already exists'}
    ]

    # .) CHECK manually if everything is set correctly -> local: [A], global: [B], urgent: []
    results += testing.check_queues(5, [call_id_A], [call_id_B], [])

    # T2) sleep for (5 seconds) now at t=5
    time.sleep(5)

    # .) Add [local C] and [global D]
    timestamp = datetime.now()
    status_1 = enqueue.enqueue(call_id_C)['status']
    status_2 = enqueue.enqueue(call_id_D)['status']

    results += [
        {'name': 'Test 6 (local add)', 'result': status_1 == 'ok'},
        {'name': 'Test 6 (global add)', 'result': status_2 == 'ok'}
    ]

    # .) CHECK manually if everything is set correctly -> local: [A, C], global: [B, D], urgent: []
    results += testing.check_queues(7, [call_id_A, call_id_C], [call_id_B, call_id_D], [])

    # T3) sleep for (5 seconds) now at t=10
    time.sleep(5)

    # .) CHECK manually if everything is set correctly -> local: [A, C], global: [A, B, D], urgent: []
    results += testing.check_queues(8, [call_id_A, call_id_C], [call_id_A, call_id_B, call_id_D], [])

    # T4) sleep for (6 seconds) now at t=16
    time.sleep(6)

    # .) CHECK manually if everything is set correctly -> local: [A, C], global: [A, B, C, D], urgent: [A, B]
    results += testing.check_queues(9, [call_id_A, call_id_C], [call_id_A, call_id_B, call_id_C, call_id_D], [call_id_A, call_id_B])

    # T5) sleep for (5 seconds) now at t=21
    time.sleep(5)

    # .) CHECK manually if everything is set correctly -> local: [A, C], global: [A, B, C, D], urgent: [A, B, C, D]
    results += testing.check_queues(10, [call_id_A, call_id_C], [call_id_A, call_id_B, call_id_C, call_id_D], [call_id_A, call_id_B, call_id_C, call_id_D])


    # Test End) EMPTY all queues
    calls_collection.delete_many({'_id': {'$in': [ObjectId(call_id) for call_id in [call_id_A, call_id_B, call_id_C, call_id_D]]}})
    call_queue.delete_many({'_id': {'$in': [ObjectId(call_id) for call_id in [call_id_A, call_id_B, call_id_C, call_id_D]]}})

    return results


if __name__ == '__main__':
    results = test_enqueue()

    for result in results:
        print(result)
