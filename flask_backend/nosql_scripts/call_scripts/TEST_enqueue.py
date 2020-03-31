
from flask_backend import status, local_queue, global_queue, urgent_queue
from flask_backend.nosql_scripts.call_scripts import enqueue, support_functions
from datetime import datetime
import time

"""
This test script test the functions:
 - add_call_to_queue
 - update_queues
"""
def test_enqueue():

    local_timeout = 15  # 7.5 seconds
    global_timeout = 30  # 15 seconds

    def update_queues():
        enqueue.update_queues(local_queue_waiting_time=local_timeout, global_queue_waiting_time=global_timeout, process_cooldown=True)

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
    results += support_functions.check_queues(2, ["A"], ["B"], [])

    # .) Call update_queues
    update_queues()

    # .) CHECK manually if everything is set correctly -> local: [A], global: [B], urgent: []
    results += support_functions.check_queues(3, ["A"], ["B"], [])

    # .) Add [local A] and [global A] (both are invalid but non-breaking operations)
    timestamp = datetime.now()
    status_1 = enqueue.add_call_to_queue("A", True, timestamp)["status"]
    status_2 = enqueue.add_call_to_queue("A", False, timestamp)["status"]

    results += [
        {"name": "Test 4 (local duplicate add)", "result": status_1 == "call id already exists"},
        {"name": "Test 4 (global duplicate add)", "result": status_2 == "call id already exists"}
    ]

    # .) CHECK manually if everything is set correctly -> local: [A], global: [B], urgent: []
    results += support_functions.check_queues(5, ["A"], ["B"], [])





    # T2) sleep for (10 seconds) now at t=10
    time.sleep(10)

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
    results += support_functions.check_queues(7, ["A", "C"], ["B", "D"], [])




    # T3) sleep for (10 seconds) now at t=20
    time.sleep(10)

    # .) Call update_queues
    update_queues()

    # .) CHECK manually if everything is set correctly -> local: [A, C], global: [A, B, D], urgent: []
    results += support_functions.check_queues(8, ["A", "C"], ["A", "B", "D"], [])




    # T4) sleep for (12 seconds) now at t=32
    time.sleep(12)

    # .) Call update_queues
    update_queues()

    # .) CHECK manually if everything is set correctly -> local: [A, C], global: [A, B, C, D], urgent: [A, B]
    results += support_functions.check_queues(9, ["A", "C"], ["A", "B", "C", "D"], ["A", "B"])




    # T5) sleep for (10 seconds) now at t=42
    time.sleep(10)

    # .) Call update_queues
    update_queues()

    # .) CHECK manually if everything is set correctly -> local: [A, C], global: [A, B, C, D], urgent: [A, B, C, D]
    results += support_functions.check_queues(10, ["A", "C"], ["A", "B", "C", "D"], ["A", "B", "C", "D"])




    # Test End) EMPTY all queues
    local_queue.delete_many({})
    global_queue.delete_many({})
    urgent_queue.delete_many({})

    return results







if __name__ == "__main__":
    results = test_enqueue()

    for result in results:
        print(result)
