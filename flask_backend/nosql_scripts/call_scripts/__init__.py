
from flask_backend import status, caller_accounts_collection, calls_collection, helper_accounts_collection
from datetime import datetime


# These scripts will just be used internally!


def add_caller(phone_number, zip_code, language):

    existing_caller = caller_accounts_collection.find_one({"phone_number": phone_number})

    if existing_caller is None:
        new_caller = {
            "phone_number": phone_number,
            "zip_code": zip_code,
            "language": language
        }
        caller_id = caller_accounts_collection.insert_one(new_caller).inserted_id
    else:
        caller_accounts_collection.update_one({"phone_number": phone_number},
                                              {"$set": {"zip_code": zip_code,
                                                        "language": language
                                                        }})
        caller_id = existing_caller["_id"]

    return status("ok", caller_id=caller_id)


def add_call(caller_id, local):
    # local is boolean
    new_call = {
        "caller_id": caller_id,
        "local": local,

        "feedback_granted": False,
        "confirmed": False,

        "helper_id": 0,
        "status": "pending",

        "timestamp_received": datetime.now()
    }
    call_id = calls_collection.insert_one(new_call).inserted_id

    return status("ok", call_id=call_id)


def modify_call(call_id, feedback_granted=None, confirmed=None):
    call = calls_collection.find_one({"_id": call_id})

    if call is None:
        return {"status": "call_id invalid"}
    else:
        call_update = {}

        if feedback_granted is not None:
            call_update.update({"feedback_granted": feedback_granted})

        if confirmed is not None:
            if confirmed:
                # add call to the callers calls list
                caller_accounts_collection.update_one({"_id": call["caller_id"]}, {"$push": {"calls": call_id}})

                call_update.update({"confirmed": True})
            else:
                # abandon call
                calls_collection.delete_one({"_id": call_id})

        if len(call_update) != 0:
            calls_collection.update_one({"_id": call_id}, {"$set": call_update})

        return status("ok")


def accept_call(call_id, helper_id):
    # call_id and agent_id are assumed to be valid

    # Change call status
    call_update = {
        "status": "accepted",
        "helper_id": helper_id,
        "timestamp_accepted": datetime.now()
    }
    calls_collection.update_one({"_id": call_id}, {"$set": call_update})

    # Add call to agent's call list
    helper_accounts_collection.update_one({"_id": helper_id}, {"$push": {"calls": call_id}})


def fulfill_call(call_id):
    # call_id and agent_id are assumed to be valid

    # Change call status
    call_update = {
        "status": "fulfilled",
        "timestamp_fulfilled": datetime.now()
    }
    calls_collection.update_one({"_id": call_id}, {"$set": call_update})


def reject_call(call_id):
    # call_id and agent_id are assumed to be valid
    call = calls_collection.find_one({"_id": call_id})

    # Change call status
    call_update = {
        "status": "pending",
        "helper_id": 0,
    }
    calls_collection.update_one({"_id": call_id}, {"$set": call_update})

    # Remove call from agent's call list
    helper_accounts_collection.update_one({"_id": call["helper_id"]}, {"pull": {"calls": call_id}})
