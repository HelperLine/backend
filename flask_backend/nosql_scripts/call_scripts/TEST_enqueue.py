
from flask_backend import status, local_queue, global_queue, urgent_queue
from flask_backend.nosql_scripts.call_scripts import enqueue
from datetime import datetime
import time

def records_to_list(records):
    # in: [{"call_id": "A"}, {"call_id": "B"}]
    # out: ["A", "B"]
    return [record["call_id"] for record in records]


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
    result_1 = {
        "name": f"Test {test_no} (local queue)",
        "result": lists_match(desired_local_list, records_to_list(list(local_queue.find({}, {"_id": 0, "call_id": 1})))),
    }
    if not result_1["result"]:
        result_1.update({"details": f"{records_to_list(list(local_queue.find({}, {'_id': 0})))} != {desired_local_list}"})

    result_2 = {
        "name": f"Test {test_no} (global queue)",
        "result": lists_match(desired_global_list,
                              records_to_list(list(global_queue.find({}, {"_id": 0, "call_id": 1})))),
    }
    if not result_2["result"]:
        result_2.update({"details": f"{records_to_list(list(global_queue.find({}, {'_id': 0})))} != {desired_global_list}"})

    result_3 = {
        "name": f"Test {test_no} (urgent queue)",
        "result": lists_match(desired_urgent_list,
                              records_to_list(list(urgent_queue.find({}, {"_id": 0, "call_id": 1})))),
    }
    if not result_3["result"]:
        result_3.update({"details": f"{records_to_list(list(urgent_queue.find({}, {'_id': 0})))} != {desired_urgent_list}"})

    return [result_1, result_2, result_3]


"""
This test script test the functions:
 - add_call_to_queue
 - update_queues
"""
def test_enqueue():

    local_timeout = 7.5  # 7.5 seconds
    global_timeout = 15  # 15 seconds

    def update_queues():
        enqueue.update_queues(local_queue_waiting_time=local_timeout, global_queue_waiting_time=global_timeout, process_cooldown=False)


    results = []


    # Test Start) EMPTY all queues
    local_queue.delete_many({})
    global_queue.delete_many({})
    urgent_queue.delete_many({})





    # T1) Add [local A] and [global B]
    timestamp = datetime.now()
    status_1 = enqueue.add_call_to_queue("A", True, timestamp)["status"]
    status_2 = enqueue.add_call_to_queue("B", False, timestamp)["status"]

    results += [
        {"name": "Test 1 (local add)", "result": status_1 == "ok"},
        {"name": "Test 1 (global add)", "result": status_2 == "ok"}
    ]

    # .) CHECK manually if everything is set correctly -> local: [A], global: [B], urgent: []
    results += check_queues(2, ["A"], ["B"], [])

    # .) Call update_queues
    update_queues()

    # .) CHECK manually if everything is set correctly -> local: [A], global: [B], urgent: []
    results += check_queues(3, ["A"], ["B"], [])

    # .) Add [local A] and [global A] (both are invalid but non-breaking operations)
    timestamp = datetime.now()
    status_1 = enqueue.add_call_to_queue("A", True, timestamp)["status"]
    status_2 = enqueue.add_call_to_queue("A", False, timestamp)["status"]

    results += [
        {"name": "Test 4 (local duplicate add)", "result": status_1 == "call id already exists"},
        {"name": "Test 4 (global duplicate add)", "result": status_2 == "call id already exists"}
    ]

    # .) CHECK manually if everything is set correctly -> local: [A], global: [B], urgent: []
    results += check_queues(5, ["A"], ["B"], [])





    # T2) sleep for (5 seconds) now at t=5
    time.sleep(5)

    # .) Add [local C] and [global D]
    timestamp = datetime.now()
    status_1 = enqueue.add_call_to_queue("C", True, timestamp)["status"]
    status_2 = enqueue.add_call_to_queue("D", False, timestamp)["status"]

    results += [
        {"name": "Test 6 (local add)", "result": status_1 == "ok"},
        {"name": "Test 6 (global add)", "result": status_2 == "ok"}
    ]

    # .) Call update_queues
    update_queues()

    # .) CHECK manually if everything is set correctly -> local: [A, C], global: [B, D], urgent: []
    results += check_queues(7, ["A", "C"], ["B", "D"], [])




    # T3) sleep for (5 seconds) now at t=10
    time.sleep(5)

    # .) Call update_queues
    update_queues()

    # .) CHECK manually if everything is set correctly -> local: [A, C], global: [A, B, D], urgent: []
    results += check_queues(8, ["A", "C"], ["A", "B", "D"], [])




    # T4) sleep for (6 seconds) now at t=16
    time.sleep(6)

    # .) Call update_queues
    update_queues()

    # .) CHECK manually if everything is set correctly -> local: [A, C], global: [A, B, C, D], urgent: [A, B]
    results += check_queues(9, ["A", "C"], ["A", "B", "C", "D"], ["A", "B"])




    # T5) sleep for (5 seconds) now at t=21
    time.sleep(5)

    # .) Call update_queues
    update_queues()

    # .) CHECK manually if everything is set correctly -> local: [A, C], global: [A, B, C, D], urgent: [A, B, C, D]
    results += check_queues(10, ["A", "C"], ["A", "B", "C", "D"], ["A", "B", "C", "D"])




    # Test End) EMPTY all queues
    local_queue.delete_many({})
    global_queue.delete_many({})
    urgent_queue.delete_many({})

    return results







if __name__ == "__main__":
    results = test_enqueue()

    for result in results:
        print(result)
