from flask_backend import status, call_queue, calls_collection
from datetime import datetime, timedelta
import time

from flask_backend.nosql_scripts.helper_account_scripts import support_functions
from flask_backend.nosql_scripts.call_scripts.support_functions import records_to_list

# These functions will just be called internally!


def enqueue(call_id, timestamp_received=None, local=None, zip_code=None):

    if (timestamp_received is None) or (local is None) or (zip_code is None):
        call = calls_collection.find_one(
            {"_id": call_id},
            {"_id": 0, "timestamp_received": 1, "local": 1, "zip_code": 1}
        )
        if call is None:
            return status("call id invalid")

        if ("timestamp_received" not in call) or ("local" not in call):
            return status("call record invalid")

        if call["local"]:
            if ("zip_code" not in call):
                return status("call record invalid")
            else:
                zip_code = call["zip_code"]

        local = call["local"]
        timestamp_received = call["timestamp_received"]


    if call_queue.find_one({"call_id": call_id}, {"_id": 0, "call_id": 1}) is not None:
        return status("call id already exists")

    # "processing" is set to true when this call is being used in
    # some operation right now. So all operations have to block this
    # with processing = True in order to prevent multiple processes to
    # work with the same data record.

    new_call = {
        "call_id": call_id,
        "local": local,
        "zip_code": zip_code,
        "timestamp_received": timestamp_received,

        "processing": False,
        "process_token": ""
    }

    call_queue.insert_one(new_call)

    return status("ok")



if __name__ == "__main__":
    pass
