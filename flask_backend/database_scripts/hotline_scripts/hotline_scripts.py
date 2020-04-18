from flask_backend import caller_accounts_collection, calls_collection
from flask_backend.support_functions import formatting, timing

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

    return formatting.status('ok', caller_id=caller_id)


def add_call(caller_id, language, call_type='', zip_code=''):

    current_timestamp = timing.get_current_time()

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
