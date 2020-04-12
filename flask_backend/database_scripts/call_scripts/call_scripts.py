from flask_backend import caller_accounts_collection, calls_collection, helper_behavior_collection, helper_accounts_collection
from flask_backend.database_scripts.call_scripts import enqueue, dequeue
from flask_backend.support_functions import fetching, formatting

from bson.objectid import ObjectId
from pymongo import UpdateOne
from datetime import datetime


# These scripts will just be used internally!


def add_caller(phone_number):
    existing_caller = caller_accounts_collection.find_one({'phone_number': phone_number})

    if existing_caller is None:
        new_caller = {
            'phone_number': phone_number,
            'calls': []
        }
        caller_id = caller_accounts_collection.insert_one(new_caller).inserted_id
    else:
        caller_id = existing_caller['_id']

    return formatting.status('ok', caller_id=caller_id)


def add_call(caller_id, language, call_type='', zip_code=''):

    current_timestamp = datetime.utcnow()
    # local is boolean
    new_call = {
        'caller_id': ObjectId(caller_id),

        'call_type': [call_type],
        'zip_code': zip_code,
        'language': language,

        'feedback_granted': False,
        'confirmed': False,

        'helper_id': 0,
        'status': 'pending',
        'comment': '',

        'timestamp_received': current_timestamp,
        'timestamp_accepted': current_timestamp,
        'timestamp_fulfilled': current_timestamp,
    }
    call_id = calls_collection.insert_one(new_call).inserted_id

    return formatting.status('ok', call_id=call_id)


def set_feeback(call_id, feedback_granted):
    calls_collection.update_one({'_id': ObjectId(call_id)}, {'$set': {'feedback_granted': feedback_granted}})


def set_confirmed(call_id, confirmed):
    call = calls_collection.find_one({'_id': ObjectId(call_id)})

    if confirmed:
        # add call to the callers calls list
        caller_accounts_collection.update_one({'_id': ObjectId(call['caller_id'])},
                                              {'$push': {'calls': ObjectId(call_id)}})
        calls_collection.update_one({'_id': ObjectId(call_id)}, {'$set': {'confirmed': True}})
    else:
        calls_collection.delete_one({'_id': ObjectId(call_id)})


def accept_call(params_dict):
    # call_id and agent_id are assumed to be valid

    helper = helper_accounts_collection.find_one({'email': params_dict['email']})

    if helper is None:
        return formatting.status('server error: helper record not found after successful authentication')

    if 'filter_type_local' not in params_dict or 'filter_type_global' not in params_dict or \
            'filter_language_german' not in params_dict or 'filter_language_english' not in params_dict:
        return formatting.status('filter parameters missing')

    dequeue_result = dequeue.dequeue(
        str(helper['_id']),
        zip_code=helper['zip_code'],
        only_local_calls=params_dict['filter_type_local'],
        only_global_calls=params_dict['filter_type_global'],
        accept_german=params_dict['filter_language_german'],
        accept_english=params_dict['filter_language_english']
    )

    if dequeue_result['status'] != 'ok':
        return dequeue_result
    else:
        return fetching.get_all_helper_data(email=params_dict['email'])


def fulfill_call(call_id, helper_id):
    # call_id and agent_id are assumed to be valid

    current_timestamp = datetime.utcnow()

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
        'timestamp': datetime.utcnow(),
        'action': 'rejected',
    }
    helper_behavior_collection.insert_one(new_behavior_log)


def comment_call(call_id, comment):
    calls_collection({'_id': ObjectId(call_id)}, {'$set': {'comment': comment}})


if __name__ == '__main__':
    call_id = '5e81e00cc40e18001ea76912'
    calls_collection.update_one({'_id': ObjectId(call_id)}, {'$set': {'feedback_granted': True}})
    print(calls_collection.find_one({'_id': ObjectId(call_id)}))
