from flask_backend import status, call_queue, calls_collection

# These functions will just be called internally!
from bson import ObjectId


def enqueue(call_id):

    call = calls_collection.find_one({'_id': ObjectId(call_id)})

    if call is None:
        return status('call id invalid')

    if call_queue.find_one({'call_id': ObjectId(call_id)}, {'_id': 0, 'call_id': 1}) is not None:
        return status('call already in queue')

    if ('language' not in call) or ('local' not in call) or \
            ('zip_code' not in call) or ('timestamp_received' not in call):
        return status('call record invalid')

    language = call['language']
    local = call['local']
    zip_code = call['zip_code']
    timestamp_received = call['timestamp_received']

    # 'processing' is set to true when this call is being used in
    # some operation right now. So all operations have to block this
    # with processing = True in order to prevent multiple processes to
    # work with the same data record.
    #
    # Exception: (Bulk) Operations that are completed immediately
    # -> That is actually the goal for every operation

    new_call = {
        'call_id': ObjectId(call_id),

        'local': local,
        'zip_code': zip_code,
        'language': language,

        'timestamp_received': timestamp_received,
    }

    call_queue.insert_one(new_call)

    return status('ok')



if __name__ == '__main__':
    pass
