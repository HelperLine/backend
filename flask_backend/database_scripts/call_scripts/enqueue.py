
from flask_backend import call_queue, calls_collection
from flask_backend.support_functions import formatting

from bson import ObjectId


def enqueue(call_id):

    call = calls_collection.find_one({'_id': ObjectId(call_id)})

    if call is None:
        return formatting.status('call_id invalid')

    if call_queue.find_one({'call_id': ObjectId(call_id)}, {'_id': 0, 'call_id': 1}) is not None:
        return formatting.status('call already in queue')

    if ('language' not in call) or ('call_type' not in call) or \
            ('zip_code' not in call) or ('timestamp_received' not in call):
        return formatting.status('call record invalid')

    new_call = {
        'call_id': ObjectId(call_id),

        'call_type': call['call_type'],
        'zip_code': call['zip_code'],
        'language': call['language'],

        'timestamp_received': call['timestamp_received'],
    }

    call_queue.insert_one(new_call)

    return formatting.status('ok')



if __name__ == '__main__':
    pass
