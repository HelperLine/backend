
from flask_backend import status, caller_accounts_collection, calls_collection, helper_accounts_collection
from datetime import datetime


from bson.objectid import ObjectId
# These scripts will just be used internally!


def add_caller(phone_number, zip_code, language):

    existing_caller = caller_accounts_collection.find_one({"phone_number": phone_number})

    if existing_caller is None:
        new_caller = {
            "phone_number": phone_number,
            "zip_code": zip_code,
            "language": language,
            "calls": []
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


def set_feeback(call_id, feedback_granted):
    print(f"Setting feedback to {feedback_granted}, call_id={call_id}")
    calls_collection.update_one({"_id": ObjectId(call_id)}, {"$set": {"feedback_granted": feedback_granted}})


def set_confirmed(call_id, confirmed):
    call = calls_collection.find_one({"_id": ObjectId(call_id)})

    print(f"call= {call}")

    if confirmed:
        # add call to the callers calls list
        caller_accounts_collection.update_one({"_id": ObjectId(call["caller_id"])}, {"$push": {"calls": call_id}})
        calls_collection.update_one({"_id": ObjectId(call_id)}, {"$set": {"confirmed": True}})
    else:
        calls_collection.delete_one({"_id": ObjectId(call_id)})


def accept_call(call_id, helper_id):
    # call_id and agent_id are assumed to be valid

    # Change call status
    call_update = {
        "status": "accepted",
        "helper_id": helper_id,
        "timestamp_accepted": datetime.now()
    }
    calls_collection.update_one({"_id": ObjectId(call_id)}, {"$set": call_update})

    # Add call to agent's call list
    helper_accounts_collection.update_one({"_id": ObjectId(call_id)}, {"$push": {"calls": call_id}})


def fulfill_call(call_id):
    # call_id and agent_id are assumed to be valid

    # Change call status
    call_update = {
        "status": "fulfilled",
        "timestamp_fulfilled": datetime.now()
    }
    calls_collection.update_one({"_id": ObjectId(call_id)}, {"$set": call_update})


def reject_call(call_id):
    # call_id and agent_id are assumed to be valid
    call = calls_collection.find_one({"_id": ObjectId(call_id)})

    # Change call status
    call_update = {
        "status": "pending",
        "helper_id": 0,
    }
    calls_collection.update_one({"_id": ObjectId(call_id)}, {"$set": call_update})

    # Remove call from agent's call list
    helper_accounts_collection.update_one({"_id": ObjectId(call["helper_id"])}, {"$pull": {"calls": call_id}})


if __name__ == "__main__":
    call_id = "5e81e00cc40e18001ea76912"
    calls_collection.update_one({"_id": ObjectId(call_id)}, {"$set": {"feedback_granted": True}})
    print(calls_collection.find_one({"_id": ObjectId(call_id)}))