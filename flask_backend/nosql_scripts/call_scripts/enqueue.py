from flask_backend import status, local_queue, global_queue, urgent_queue, calls_collection
from datetime import datetime, timedelta
import time

from flask_backend.nosql_scripts.helper_account_scripts import support_functions

# constants
LOCAL_QUEUE_WAITING_TIME = 15 * 60
GLOBAL_QUEUE_WAITING_TIME = 45 * 60


# These functions will just be called internally!


def add_call_to_queue(call_id):
    pass


def make_local_call_also_global(call_id):
    pass


def make_local_call_also_urgent(call_id):
    pass


def update_queues():
    # After LOCAL_QUEUE_WAITING_TIME calls from the local queue also get added to the global queue
    # After GLOBAL_QUEUE_WAITING_TIME calls from the global queue also get added to the urgent queue

    # Blocking and Unblocking resolves that:
    #  - calls are duplicately added because of a parallel execution of update_queue()
    #  - calls are assigned during a transition between queues

    # When "processing" is set to true this call will not be assigned
    # When the processing happened less than 10 seconds ago this call will not be assigned

    # Once I know how to do bulk operations on multiple datasets at once I can get rid of
    # the process_timestamp and the 10 second rule

    result = status("ok")

    process_token = support_functions.generate_random_key(length=16)
    process_timestamp = datetime.now()
    time_decider_process = process_timestamp - timedelta(seconds=10)
    time_decider_local_queue = process_timestamp - timedelta(seconds=LOCAL_QUEUE_WAITING_TIME)
    time_decider_global_queue = process_timestamp - timedelta(seconds=GLOBAL_QUEUE_WAITING_TIME)

    # 1) Block records for this operation
    local_queue.update_many({"timestamp_received": {"$lt": time_decider_local_queue}, "processing": False,
                             "process_timestamp": {"$lt": time_decider_process}},
                            {"$set": {"process_token": process_token, "processing": True,
                                      "process_timestamp": process_timestamp}})

    global_queue.update_many({"timestamp_received": {"$lt": time_decider_global_queue}, "processing": False,
                              "process_timestamp": {"$lt": time_decider_process}},
                             {"$set": {"process_token": process_token, "processing": True,
                                       "process_timestamp": process_timestamp}})

    # 2) Fetch all records to be transferred between queues
    global_calls_to_be_added = list(local_queue.find({"timestamp_received": {"$lt": time_decider_local_queue,
                                                                             "$gt": time_decider_global_queue}}))

    urgent_calls_to_be_added = list(local_queue.find({"timestamp_received": {"$lt": time_decider_global_queue}}))
    urgent_calls_to_be_added += list(global_queue.find({"timestamp_received": {"$lt": time_decider_global_queue}}))

    result.update({
        "new_global_calls": len(global_calls_to_be_added),
        "new_urgent_calls": len(urgent_calls_to_be_added),
    })

    # 3) Insert these records
    if len(global_calls_to_be_added) > 0:
        global_queue.insert_many(global_calls_to_be_added)

    if len(urgent_calls_to_be_added) > 0:
        urgent_queue.insert_many(urgent_calls_to_be_added)

    # 4) Unblock records in local, global and urgent queue
    local_queue.update_many({"process_token": process_token}, {"$set": {"processing": False}})
    global_queue.update_many({"process_token": process_token}, {"$set": {"processing": False}})
    urgent_queue.update_many({"process_token": process_token}, {"$set": {"processing": False}})

    return result


if __name__ == "__main__":
    t1 = time.time()
    print(update_queues())
    t2 = time.time()

    print(f"Total: {t2 - t1} seconds")
