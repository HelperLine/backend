
from flask_backend import call_queue, helper_accounts_collection, helper_behavior_collection, calls_collection
from flask_backend.support_functions import fetching, formatting, timing

from bson import ObjectId
from pymongo import UpdateOne

# constants
local_timeout_seconds = 15 * 60
global_timeout_seconds = 45 * 60


# triggered when user clicks 'accept call'
# filter options passed as arguments!
# formatting.status with call_id is begin returned

def dequeue(helper_id, zip_code=None,
            only_local=None, only_global=None,
            german=None, english=None):

    current_timestamp = timing.get_current_time()

    if only_local and only_global:
        return formatting.status('invalid function call - only_local = only_global = True')



    # Step 1) Find the helpers zip_code

    if any([e is None] for e in [zip_code, only_local, only_global, english, german]) is None:
        helper = helper_accounts_collection.find_one({'_id': ObjectId(helper_id)})
        if helper is None:
            return formatting.status('helper_id invalid')

        zip_code = helper['zip_code'] if (zip_code is None) else zip_code
        only_local = helper['filter_type_local'] if (only_local is None) else only_local
        only_global = helper['filter_type_global'] if (only_global is None) else only_global
        german = helper['filter_language_german'] if (german is None) else german
        english = helper['filter_language_english'] if (english is None) else english

    language_list = []
    language_list += ['german'] if german else []
    language_list += ['english'] if english else []

    zip_codes_list = fetching.get_adjacent_zip_codes(zip_code) if (zip_code != '') else []

    projection_dict = {}



    # Step 2) Find Call

    if only_local:
        filter_dict = {
            'call_type': {"$elemMatch": {"$eq": 'local'}},
            'zip_code': {'$in': zip_codes_list},
            'language': {'$in': language_list}
        }
        call = call_queue.find_one_and_delete(
            filter_dict, projection_dict,
            sort=[('timestamp_received', 1)],
        )

    elif only_global:
        filter_dict = {
            'call_type': {"$elemMatch": {"$eq": 'global'}},
            'language': {'$in': language_list}
        }
        call = call_queue.find_one_and_delete(
            filter_dict, projection_dict,
            sort=[('timestamp_received', 1)],
        )

    else:
        # 1. Urgent Queue
        filter_dict = {
            'timestamp_received': {
                '$lt': timing.get_current_time(offset_seconds=-global_timeout_seconds)
            }
        }
        call = call_queue.find_one_and_delete(
            filter_dict, projection_dict,
            sort=[('timestamp_received', 1)],
        )

        # 2. Local Queue
        if call is None:
            filter_dict = {
                'call_type': {"$elemMatch": {"$eq": 'local'}},
                'zip_code': {'$in': zip_codes_list},
                'language': {'$in': language_list}
            }
            call = call_queue.find_one_and_delete(
                filter_dict, projection_dict,
                sort=[('timestamp_received', 1)],
            )

        # 3. Global Queue
        if call is None:
            # Or chain needed so that calls in other regions which
            # are not in the global queue yet get assigned
            filter_dict = {
                '$or': [
                    {
                        'call_type': {
                            "$elemMatch": {"$eq": 'local'}
                        },
                        'timestamp_received': {
                            '$lt': timing.get_current_time(offset_seconds=-local_timeout_seconds)
                        }
                    },
                    {
                        'call_type': {
                            "$elemMatch": {"$eq": 'global'}
                        }
                    }
                ]
            },
            call = call_queue.find_one_and_delete(
                filter_dict, projection_dict,
                sort=[('timestamp_received', 1)],
            )

    if call is None:
        return formatting.status('currently no call available')

    call_id = call['call_id']



    # Step 3) Update call (helper_id, formatting.status, timestamp_accepted)

    call_update_dict_1 = {
        "$set": {
            'status': 'accepted',
            'helper_id': ObjectId(helper_id),
            'timestamp_accepted': current_timestamp
        }
    }

    print(f"call = {call}")

    # accepted-match if local call was accepted from local queue (successful) or global call
    # accepted-mismatch if local call was matched with non-local helper

    if "local" in call["call_type"] and call["zip_code"] not in zip_codes_list:
        new_call_type = "accepted-mismatch"
    else:
        new_call_type = "accepted-match"

    call_update_dict_2 = {
        "$push": {
            "call_type": new_call_type,
        }
    }

    operations = [
        UpdateOne({'_id': ObjectId(call_id)}, call_update_dict_1),
        UpdateOne({'_id': ObjectId(call_id)}, call_update_dict_2)
    ]
    calls_collection.bulk_write(operations)



    # Step 4) Add helper behavior (helper_id, call_id, timestamp, action='accepted'
    new_behavior_log = {
        'helper_id': ObjectId(helper_id),
        'call_id': ObjectId(call_id),
        'timestamp': current_timestamp,
        'action': 'accepted',
    }
    helper_behavior_collection.insert_one(new_behavior_log)



    return formatting.status('ok')
