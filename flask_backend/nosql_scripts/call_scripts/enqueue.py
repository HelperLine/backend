from flask_backend import status, call_queue
from datetime import datetime, timedelta
import time

from flask_backend.nosql_scripts.helper_account_scripts import support_functions
from flask_backend.nosql_scripts.call_scripts.support_functions import records_to_list

# constants
LOCAL_QUEUE_WAITING_TIME = 15 * 60
GLOBAL_QUEUE_WAITING_TIME = 45 * 60


# These functions will just be called internally!


def enqueue(call_id, local, timestamp_received):

    if call_queue.find_one({"call_id": call_id}, {"_id": 0, "call_id": 1}) is not None:
        return status("call id already exists")

    # "processing" is set to true when this call is being used in
    # some operation right now. So all operations have to block this
    # with processing = True in order to prevent multiple processes to
    # work with the same data record.

    new_call = {
        "call_id": call_id,
        "local": local,
        "timestamp_received": timestamp_received,

        "processing": False,
    }

    call_queue.insert_one(new_call)

    return status("ok")



if __name__ == "__main__":
    pass
