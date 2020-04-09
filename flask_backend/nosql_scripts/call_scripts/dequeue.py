
from flask_backend import status, call_queue, helper_accounts_collection, helper_behavior_collection, calls_collection

from flask_backend.nosql_scripts.call_scripts import support_functions
from flask_backend.nosql_scripts.helper_account_scripts.support_functions import get_adjacent_zip_codes

from datetime import datetime
from bson import ObjectId

# triggered when user clicks 'accept call'
# filter options passed as arguments!
# status with call_id is begin returned

def dequeue(helper_id, zip_code=None,
            only_local_calls=None, only_global_calls=None,
            accept_german=None, accept_english=None):

    current_timestamp = datetime.now()

    if only_local_calls and only_global_calls:
        return status('invalid function call')



    # Step 1) Find the helpers zip_code

    if any([e is None] for e in [zip_code, only_local_calls, only_global_calls, accept_english, accept_german]) is None:
        helper = helper_accounts_collection.find_one({'_id': ObjectId(helper_id)})
        if helper is None:
            return status('helper id invalid')

        zip_code = helper['zip_code'] if (zip_code is None) else zip_code
        only_local_calls = helper['filter_type_local'] if (only_local_calls is None) else only_local_calls
        only_global_calls = helper['filter_type_global'] if (only_global_calls is None) else only_global_calls
        accept_german = helper['filter_language_german'] if (accept_german is None) else accept_german
        accept_english = helper['filter_language_english'] if (accept_english is None) else accept_english

    language_list = []
    language_list += ['german'] if accept_german else []
    language_list += ['english'] if accept_english else []

    zip_codes_list = get_adjacent_zip_codes(zip_code) if (zip_code != '') else []

    print(f'zip_code: {zip_code}')
    print(f'zip_codes: {zip_codes_list}')

    projection_dict = {
        '_id': 0,
        'call_id': 1
    }



    # Step 2) Find Call

    if only_local_calls:

        filter_dict = {
            'call_type': {"$elemMatch": {"$eq": 'local'}},
            'zip_code': {'$in': zip_codes_list},
            'language': {'$in': language_list}
        }

        call = call_queue.find_one_and_delete(
            filter_dict, projection_dict,
            sort=[('timestamp_received', 1)],
        )

    elif only_global_calls:

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
        call = call_queue.find_one_and_delete(
            {'timestamp_received': {'$lt': current_timestamp - support_functions.global_timeout_timedelta}},
            projection_dict,
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
            call = call_queue.find_one_and_delete(
                {'$or': [
                    {'call_type': {"$elemMatch": {"$eq": 'local'}}, 'timestamp_received': {'$lt': current_timestamp - support_functions.local_timeout_timedelta}},
                    {'call_type': {"$elemMatch": {"$eq": 'global'}}}
                ]},
                projection_dict,
                sort=[('timestamp_received', 1)],
            )

    if call is None:
        return status('currently no call available')

    call_id = call['call_id']



    # Step 3) Update call (helper_id, status, timestamp_accepted)
    calls_collection.update_one(
        {'_id': ObjectId(call_id)},
        {'$set': {'helper_id': ObjectId(helper_id), 'status': 'accepted', 'timestamp_accepted': current_timestamp}})


    # Step 4) Add helper behavior (helper_id, call_id, timestamp, action='accepted'
    new_behavior_log = {
        'helper_id': ObjectId(helper_id),
        'call_id': ObjectId(call_id),
        'timestamp': current_timestamp,
        'action': 'accepted',
    }
    helper_behavior_collection.insert_one(new_behavior_log)



    return status('ok')
