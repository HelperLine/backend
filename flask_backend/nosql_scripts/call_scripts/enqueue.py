from flask_backend import status, local_queue, global_queue, urgent_queue, calls_collection
from datetime import datetime, timedelta
import time

from flask_backend.nosql_scripts.helper_account_scripts import support_functions

# constants
LOCAL_QUEUE_WAITING_TIME = 15 * 60
GLOBAL_QUEUE_WAITING_TIME = 45 * 60


# These functions will just be called internally!

def records_to_list(records):
    # in: [{"call_id": "A"}, {"call_id": "B"}]
    # out: ["A", "B"]
    return [record["call_id"] for record in records]


def add_call_to_queue(call_id, local, timestamp_received):
    call_id_exists = local_queue.find_one({"call_id": call_id}, {"_id": 0, "call_id": 1}) is not None

    # avoid unnecessary database calls
    if not call_id_exists:
        call_id_exists = global_queue.find_one({"call_id": call_id}, {"_id": 0, "call_id": 1}) is not None

    if call_id_exists:
        return status("call id already exists")

    process_timestamp = datetime.now()
    new_call = {
        "call_id": call_id,
        "local": local,
        "timestamp_received": timestamp_received,

        "processing": False,
        "process_timestamp": process_timestamp
    }

    if local:
        local_queue.insert_one(new_call)
    else:
        global_queue.insert_one(new_call)

    return status("ok")


def update_queues(local_queue_waiting_time=LOCAL_QUEUE_WAITING_TIME,
                  global_queue_waiting_time=GLOBAL_QUEUE_WAITING_TIME, process_cooldown=True):
    # After LOCAL_QUEUE_WAITING_TIME calls from the local queue also get added to the global queue
    # After GLOBAL_QUEUE_WAITING_TIME calls from the global queue also get added to the urgent queue

    # Blocking and Unblocking resolves that:
    #  - calls are duplicately added because of a parallel execution of update_queue()
    #  - calls are assigned during a transition between queues

    # When "processing" is set to true this call will not be assigned
    # When the processing happened less than 5 seconds ago this call will not be assigned

    # Once I know how to do bulk operations on multiple datasets at once I can get rid of
    # the process_timestamp and the 5 second rule

    result = status("ok")

    process_token = support_functions.generate_random_key(length=16)
    process_timestamp = datetime.now()
    time_decider_process = process_timestamp - timedelta(seconds=5)
    time_decider_local_queue = process_timestamp - timedelta(seconds=local_queue_waiting_time)
    time_decider_global_queue = process_timestamp - timedelta(seconds=global_queue_waiting_time)

    # 1) Block records for this operation
    if process_cooldown:
        local_queue.update_many({"timestamp_received": {"$lt": time_decider_local_queue}, "processing": False,
                                 "process_timestamp": {"$lt": time_decider_process}},
                                {"$set": {"process_token": process_token, "processing": True,
                                          "process_timestamp": process_timestamp}})

        global_queue.update_many({"timestamp_received": {"$lt": time_decider_global_queue}, "processing": False,
                                  "process_timestamp": {"$lt": time_decider_process}},
                                 {"$set": {"process_token": process_token, "processing": True,
                                           "process_timestamp": process_timestamp}})
    else:
        local_queue.update_many({"timestamp_received": {"$lt": time_decider_local_queue}, "processing": False},
                                {"$set": {"process_token": process_token, "processing": True,
                                          "process_timestamp": process_timestamp}})

        global_queue.update_many({"timestamp_received": {"$lt": time_decider_global_queue}, "processing": False},
                                 {"$set": {"process_token": process_token, "processing": True,
                                           "process_timestamp": process_timestamp}})

    # 2) Fetch all records to be transferred between queues
    existing_global_call_ids = records_to_list(list(global_queue.find({}, {"_id": 0, "call_id": 1})))
    existing_urgent_call_ids = records_to_list(list(urgent_queue.find({}, {"_id": 0, "call_id": 1})))

    all_global_calls = list(local_queue.find({"timestamp_received": {"$lt": time_decider_local_queue,
                                                                     "$gt": time_decider_global_queue}},
                                             {"_id": 0}))

    all_urgent_calls = list(local_queue.find({"timestamp_received": {"$lt": time_decider_global_queue}}, {"_id": 0}))
    all_urgent_calls += list(global_queue.find({"timestamp_received": {"$lt": time_decider_global_queue},
                                                "call_id": {"$nin": [call["call_id"] for call in all_urgent_calls]}},
                                               {"_id": 0}))

    global_calls_to_be_added = []
    urgent_calls_to_be_added = []

    for call in all_global_calls:
        if call["call_id"] not in existing_global_call_ids:
            global_calls_to_be_added.append(call)

    for call in all_urgent_calls:
        if call["call_id"] not in existing_urgent_call_ids:
            urgent_calls_to_be_added.append(call)

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
