from flask_backend import status, call_queue, calls_collection
from flask_backend.nosql_scripts.call_scripts import enqueue, support_functions
from datetime import datetime, timedelta
import time


from bson import ObjectId


def check_queues(test_no, desired_local_list, desired_global_list, desired_urgent_list):
    current_timestamp = datetime.now()

    local_calls = list(call_queue.find(
        {"local": True},
        {"_id": 0, "call_id": 1}))

    global_calls = list(call_queue.find(
        {"local": True, "timestamp_received": {"$lt": current_timestamp - support_functions.local_timeout_timedelta}},
        {"_id": 0, "call_id": 1}))
    global_calls += list(call_queue.find(
        {"local": False},
        {"_id": 0, "call_id": 1}))

    urgent_calls = list(call_queue.find(
        {"timestamp_received": {"$lt": current_timestamp - support_functions.global_timeout_timedelta}},
        {"_id": 0, "call_id": 1}))


    result_1 = {
        "name": f"Test {test_no} (local queue)",
        "result": support_functions.lists_match(desired_local_list, support_functions.records_to_list(local_calls)),
    }
    if not result_1["result"]:
        result_1.update({"details": f"{support_functions.records_to_list(local_calls)} != {desired_local_list}"})

    result_2 = {
        "name": f"Test {test_no} (global queue)",
        "result": support_functions.lists_match(desired_global_list, support_functions.records_to_list(global_calls)),
    }
    if not result_2["result"]:
        result_2.update({"details": f"{support_functions.records_to_list(global_calls)} != {desired_global_list}"})

    result_3 = {
        "name": f"Test {test_no} (urgent queue)",
        "result": support_functions.lists_match(desired_urgent_list, support_functions.records_to_list(urgent_calls)),
    }
    if not result_3["result"]:
        result_3.update({"details": f"{support_functions.records_to_list(urgent_calls)} != {desired_urgent_list}"})

    return [result_1, result_2, result_3]


"""
This test script test the functions:
 - add_call_to_queue
 - update_queues
"""


def test_enqueue():

    results = []

    # Test Start) EMPTY all queues
    calls_collection.delete_many({})
    call_queue.delete_many({})

    call_id_A = calls_collection.insert_one({
        "timestamp_received": datetime.now(),
        "local": True,
        "zip_code": "80000"
    }).inserted_id

    call_id_B = calls_collection.insert_one({
        "timestamp_received": datetime.now(),
        "local": False,
        "zip_code": "80000"
    }).inserted_id

    call_id_C = calls_collection.insert_one({
        "timestamp_received": datetime.now() + timedelta(seconds=5),
        "local": True,
        "zip_code": "80000"
    }).inserted_id

    call_id_D = calls_collection.insert_one({
        "timestamp_received": datetime.now() + timedelta(seconds=5),
        "local": False,
        "zip_code": "80000"
    }).inserted_id


    # T1) Add [local A] and [global B]
    timestamp = datetime.now()
    status_1 = enqueue.enqueue(call_id_A)["status"]
    status_2 = enqueue.enqueue(call_id_B)["status"]

    results += [
        {"name": "Test 1 (local add)", "result": status_1 == "ok"},
        {"name": "Test 1 (global add)", "result": status_2 == "ok"}
    ]

    # .) CHECK manually if everything is set correctly -> local: [A], global: [B], urgent: []
    results += check_queues(2, [call_id_A], [call_id_B], [])

    # .) Add [local A] and [global B] (both are invalid but non-breaking operations)
    timestamp = datetime.now()
    status_1 = enqueue.enqueue(call_id_A)["status"]
    status_2 = enqueue.enqueue(call_id_B)["status"]

    results += [
        {"name": "Test 4 (local duplicate add)", "result": status_1 == "call id already exists"},
        {"name": "Test 4 (global duplicate add)", "result": status_2 == "call id already exists"}
    ]

    # .) CHECK manually if everything is set correctly -> local: [A], global: [B], urgent: []
    results += check_queues(5, [call_id_A], [call_id_B], [])

    # T2) sleep for (5 seconds) now at t=5
    time.sleep(5)

    # .) Add [local C] and [global D]
    timestamp = datetime.now()
    status_1 = enqueue.enqueue(call_id_C)["status"]
    status_2 = enqueue.enqueue(call_id_D)["status"]

    results += [
        {"name": "Test 6 (local add)", "result": status_1 == "ok"},
        {"name": "Test 6 (global add)", "result": status_2 == "ok"}
    ]

    # .) CHECK manually if everything is set correctly -> local: [A, C], global: [B, D], urgent: []
    results += check_queues(7, [call_id_A, call_id_C], [call_id_B, call_id_D], [])

    # T3) sleep for (5 seconds) now at t=10
    time.sleep(5)

    # .) CHECK manually if everything is set correctly -> local: [A, C], global: [A, B, D], urgent: []
    results += check_queues(8, [call_id_A, call_id_C], [call_id_A, call_id_B, call_id_D], [])

    # T4) sleep for (6 seconds) now at t=16
    time.sleep(6)

    # .) CHECK manually if everything is set correctly -> local: [A, C], global: [A, B, C, D], urgent: [A, B]
    results += check_queues(9, [call_id_A, call_id_C], [call_id_A, call_id_B, call_id_C, call_id_D], [call_id_A, call_id_B])

    # T5) sleep for (5 seconds) now at t=21
    time.sleep(5)

    # .) CHECK manually if everything is set correctly -> local: [A, C], global: [A, B, C, D], urgent: [A, B, C, D]
    results += check_queues(10, [call_id_A, call_id_C], [call_id_A, call_id_B, call_id_C, call_id_D], [call_id_A, call_id_B, call_id_C, call_id_D])


    # Test End) EMPTY all queues
    calls_collection.delete_many({"_id": {"$in": [ObjectId(call_id) for call_id in [call_id_A, call_id_B, call_id_C, call_id_D]]}})
    call_queue.delete_many({"_id": {"$in": [ObjectId(call_id) for call_id in [call_id_A, call_id_B, call_id_C, call_id_D]]}})

    return results


if __name__ == "__main__":
    results = test_enqueue()

    for result in results:
        print(result)
