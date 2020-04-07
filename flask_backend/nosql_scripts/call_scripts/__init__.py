
from flask_backend import status, caller_accounts_collection, calls_collection, helper_accounts_collection, helper_behavior_collection
from datetime import datetime

from flask_backend.nosql_scripts.call_scripts import enqueue, dequeue
from flask_backend.nosql_scripts.helper_account_scripts.support_functions import get_all_helper_data

from bson.objectid import ObjectId
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

    return status('ok', caller_id=caller_id)


def add_call(caller_id, language, local=False, zip_code=''):
    # local is boolean
    new_call = {
        'caller_id': ObjectId(caller_id),

        'local': local,
        'zip_code': zip_code,
        'language': language,

        'feedback_granted': False,
        'confirmed': False,

        'helper_id': 0,
        'status': 'pending',
        'comment': '',

        'timestamp_received': datetime.now(),
        'timestamp_accepted': datetime.now(),
        'timestamp_fulfilled': datetime.now(),
    }
    call_id = calls_collection.insert_one(new_call).inserted_id

    return status('ok', call_id=call_id)


def set_feeback(call_id, feedback_granted):
    calls_collection.update_one({'_id': ObjectId(call_id)}, {'$set': {'feedback_granted': feedback_granted}})


def set_confirmed(call_id, confirmed):
    call = calls_collection.find_one({'_id': ObjectId(call_id)})

    if confirmed:
        # add call to the callers calls list
        caller_accounts_collection.update_one({'_id': ObjectId(call['caller_id'])}, {'$push': {'calls': ObjectId(call_id)}})
        calls_collection.update_one({'_id': ObjectId(call_id)}, {'$set': {'confirmed': True}})

        print(enqueue.enqueue(call_id))
    else:
        calls_collection.delete_one({'_id': ObjectId(call_id)})


def accept_call(helper_id, zip_code,
                only_local_calls, only_global_calls,
                accept_german, accept_english):

    # call_id and agent_id are assumed to be valid

    dequeue_result = dequeue.dequeue(helper_id=helper_id,
                                     only_local_calls=only_local_calls,
                                     only_global_calls=only_global_calls,
                                     accept_german=accept_german)

    if dequeue_result['status'] != 'ok':
        return dequeue_result
    else:
        return get_all_helper_data(helper_id=helper_id)


def fulfill_call(call_id, helper_id):
    # call_id and agent_id are assumed to be valid

    current_timestamp = datetime.now()

    # Change call status
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

    # Remove call from agent's call list
    helper_accounts_collection.update_one({'_id': ObjectId(helper_id)}, {'$pull': {'calls': ObjectId(call_id)}})

    # Change call status
    call_update = {
        'status': 'pending',
        'helper_id': 0,
    }
    calls_collection.update_one({'_id': ObjectId(call_id)}, {'$set': call_update})
    enqueue.enqueue(call_id)

    new_behavior_log = {
        'helper_id': ObjectId(helper_id),
        'call_id': ObjectId(call_id),
        'timestamp': datetime.now(),
        'action': 'rejected',
    }
    helper_behavior_collection.insert_one(new_behavior_log)


def comment_call(call_id, comment):
    calls_collection.update_one({'_id': ObjectId(call_id)}, {'$set': {'comment': comment}})


if __name__ == '__main__':
    call_id = '5e81e00cc40e18001ea76912'
    calls_collection.update_one({'_id': ObjectId(call_id)}, {'$set': {'feedback_granted': True}})
    print(calls_collection.find_one({'_id': ObjectId(call_id)}))
