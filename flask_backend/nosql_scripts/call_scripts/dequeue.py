
from flask_backend import status, call_queue, helper_accounts_collection, helper_behavior_collection, calls_collection

from flask_backend.nosql_scripts.call_scripts import support_functions

from datetime import datetime
from bson import ObjectId

# triggered when user clicks "accept call"
# filter options passed as arguments!
# status with call_id is begin returned

def dequeue(helper_id, zip_code=None, only_local_calls=False, only_global_calls=False):

    current_timestamp = datetime.now()

    if only_local_calls and only_global_calls:
        return status("invalid function call")



    # Step 1) Find the helpers zip_code

    # If the zip_code is available we can pass it as
    # a parameter, if not it will be queried in here.
    if not only_global_calls and zip_code is None:
        helper = helper_accounts_collection.find_one({"_id": ObjectId(helper_id)}, {"_id": 0, "zip_code": 1})
        if helper is None:
            return status("helper id invalid")
        zip_code = helper["zip_code"]



    # Step 2) Find Call

    if only_local_calls:
        # noinspection PyUnboundLocalVariable
        call = call_queue.find_one_and_delete(
            {"local": True, "zip_code": zip_code},
            {"_id": 0, "call_id": 1},
            sort=[("timestamp_received", 1)],
        )

    elif only_global_calls:
        call = call_queue.find_one_and_delete(
            {"local": False},
            {"_id": 0, "call_id": 1},
            sort=[("timestamp_received", 1)],
        )

    else:
        # 1. Urgent Queue
        call = call_queue.find_one_and_delete(
            {"timestamp_received": {"$lt": current_timestamp - support_functions.global_timeout_timedelta}},
            {"_id": 0, "call_id": 1},
            sort=[("timestamp_received", 1)],
        )

        # 2. Local Queue
        if call is None:
            # noinspection PyUnboundLocalVariable
            call = call_queue.find_one_and_delete(
                {"local": True, "zip_code": zip_code},
                {"_id": 0, "call_id": 1},
                sort=[("timestamp_received", 1)],
            )

        # 3. Global Queue
        if call is None:
            # Or chain needed so that calls in other regions which
            # are not in the global queue yet get assigned
            call = call_queue.find_one_and_delete(
                {"$or": [
                    {"local": True, "timestamp_received": {"$lt": current_timestamp - support_functions.local_timeout_timedelta}},
                    {"local": False}
                ]},
                {"_id": 0, "call_id": 1},
                sort=[("timestamp_received", 1)],
            )

    if call is None:
        return status("currently no call available")

    call_id = call["call_id"]



    # Step 2) Update call (helper_id, status, timestamp_accepted)
    calls_collection.update_one(
        {"_id": ObjectId(call_id)},
        {"$set": {"helper_id": helper_id, "status": "accepted", "timestamp_accepted": current_timestamp}})


    # Step 3) Update helper (calls)
    helper_accounts_collection.update_one(
        {"_id": ObjectId(helper_id)},
        {"$push": {"calls": call_id}})



    # Step 4) Add helper behavior (helper_id, call_id, timestamp, action="accepted"
    new_behavior_log = {
        "helper_id": helper_id,
        "call_id": call_id,
        "timestamp": current_timestamp,
        "action": "accepted",
    }
    helper_behavior_collection.insert_one(new_behavior_log)



    return status("ok", call_id=call_id)

