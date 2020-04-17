from flask_backend import calls_collection, helper_behavior_collection, helper_accounts_collection
from flask_backend.database_scripts.call_scripts import dequeue
from flask_backend.database_scripts.hotline_scripts import enqueue
from flask_backend.support_functions import formatting, timing

from bson.objectid import ObjectId
from pymongo import UpdateOne
from datetime import datetime, timezone, timedelta

# These scripts will just be used internally!


def get_calls(email):
    helper_account = helper_accounts_collection.find_one({'email': email})

    if helper_account is None:
        return formatting.server_error_helper_record, 500

    match_dict = {
        'helper_id': ObjectId(helper_account['_id']),
    }

    lookup_dict = {
        'from': 'callers',
        'localField': 'caller_id',
        'foreignField': '_id',
        'as': 'caller'
    }

    project_dict = {
        '_id': 1,
        'status': 1,
        'call_type': 1,

        'timestamp_received': 1,
        'timestamp_accepted': 1,
        'timestamp_fulfilled': 1,

        'comment': 1,

        'caller': {
            'phone_number': 1
        }
    }

    raw_list = list(
        calls_collection.aggregate([
            {'$match': match_dict},
            {'$lookup': lookup_dict},
            {'$project': project_dict},
        ]))

    projected_list = [{
        'call_id': str(call['_id']),
        'status': call['status'],
        'call_type': call['call_type'],
        'timestamp_received': timing.datetime_to_string(call['timestamp_received']),
        'timestamp_accepted': timing.datetime_to_string(call['timestamp_accepted']),
        'timestamp_fulfilled': timing.datetime_to_string(call['timestamp_fulfilled']),
        'comment': call['comment'],
        'phone_number': call['caller'][0]['phone_number']
    } for call in raw_list]

    accepted_calls_list = list(filter(lambda x: x['status'] == 'accepted', projected_list))
    accepted_calls_list.sort(key=(lambda x: x["timestamp_accepted"]), reverse=True)

    fulfilled_calls_list = list(filter(lambda x: x['status'] == 'fulfilled', projected_list))
    fulfilled_calls_list.sort(key=(lambda x: x["timestamp_fulfilled"]), reverse=True)

    calls_result = {
        'accepted': accepted_calls_list,
        'fulfilled': fulfilled_calls_list,
    }

    return formatting.status("ok", calls=calls_result)


def accept_call(params_dict):
    # call_id and helper_id are assumed to be valid

    helper = helper_accounts_collection.find_one({'email': params_dict['email']})

    if helper is None:
        return formatting.server_error_helper_record

    dequeue_result = dequeue.dequeue(
        str(helper['_id']),
        zip_code=helper['account']['zip_code'],
        only_local_calls=params_dict['filter']['call_type']['only_local'],
        only_global_calls=params_dict['filter']['call_type']['only_global'],
        accept_german=params_dict['filter']['language']['german'],
        accept_english=params_dict['filter']['language']['english']
    )

    return dequeue_result


def modify_call(params_dict):

    # Step 1) Check database correctness

    helper = helper_accounts_collection.find_one({"email": params_dict["email"]})
    if helper is None:
        return formatting.server_error_helper_record

    call = calls_collection.find_one({"_id": ObjectId(params_dict['call']["call_id"])})

    if call is None:
        return formatting.status("call_id invalid")



    # Step 2) Check eligibility to modify this call

    if str(call["helper_id"]) != str(helper["_id"]):
        return formatting.status("not authorized to edit this call")

    if (call["status"] == "fulfilled") and (params_dict['call']["action"] in ["reject", "fulfill"]):
        return formatting.status('cannot change a fulfilled call')



    # Step 2) Actually edit the call

    if params_dict['call']["action"] == "fulfill":
        fulfill_call(params_dict['call']["call_id"], helper["_id"])

    elif params_dict['call']["action"] == "reject":
        reject_call(params_dict['call']["call_id"], helper["_id"])

    elif params_dict['call']["action"] == "comment":
        comment_call(params_dict['call']["call_id"], params_dict['call']["comment"])

    return formatting.status("ok")


def fulfill_call(call_id, helper_id):
    # call_id and agent_id are assumed to be valid

    current_timestamp = datetime.now(timezone(timedelta(hours=2)))

    # Change call formatting.status
    call_update = {
        'status': 'fulfilled',
        'timestamp_fulfilled': current_timestamp
    }
    calls_collection.update_one({'_id': ObjectId(call_id)}, {'$set': call_update})

    new_behavior_log = {
        'helper_id': ObjectId(helper_id),
        'call_id': ObjectId(call_id),
        'timestamp': current_timestamp,
        'action': 'fulfilled',
    }
    helper_behavior_collection.insert_one(new_behavior_log)


def reject_call(call_id, helper_id):
    # Change call formatting.status
    call_update_dict_1 = {
        "$set": {
            'status': 'pending',
            'helper_id': 0,
            'comment': '',
        }
    }

    # accepted-match if local call was accepted from local queue (successful)
    # accepted-mismatch if local call was accepted from global/urgent queue (not successful)

    call_update_dict_2 = {
        "$pull": {
            "call_type": {"$in": ["forwarded", "accepted-match", "accepted-mismatch"]},
        }
    }

    operations = [
        UpdateOne({"_id": ObjectId(call_id)}, call_update_dict_1),
        UpdateOne({"_id": ObjectId(call_id)}, call_update_dict_2)
    ]
    calls_collection.bulk_write(operations)

    enqueue.enqueue(call_id)

    new_behavior_log = {
        'helper_id': ObjectId(helper_id),
        'call_id': ObjectId(call_id),
        'timestamp': datetime.now(timezone(timedelta(hours=2))),
        'action': 'rejected',
    }
    helper_behavior_collection.insert_one(new_behavior_log)


def comment_call(call_id, comment):
    calls_collection.update_one({'_id': ObjectId(call_id)}, {'$set': {'comment': comment}})


if __name__ == '__main__':
    call_id = '5e81e00cc40e18001ea76912'
    calls_collection.update_one({'_id': ObjectId(call_id)}, {'$set': {'feedback_granted': True}})
    print(calls_collection.find_one({'_id': ObjectId(call_id)}))
