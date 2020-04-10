
from flask_backend import status, helper_accounts_collection, phone_tokens_collection
from flask_backend.support_functions import tokening, fetching

from pymongo import DeleteMany, InsertOne
from datetime import datetime, timedelta
from bson import ObjectId


def verify_phone_number(token='', phone_number=''):

    print({
        'token': token,
        'phone_number': phone_number
    })
    record = phone_tokens_collection.find_one(
        {
            'token': token,
            'timestamp_issued': {'$gt': datetime.now() - timedelta(minutes=3)},
        })


    if record is None:
        return status('token invalid')

    helper_id = record['helper_id']

    helper_accounts_collection.update_one(
        {'_id': ObjectId(helper_id)},
        {'$set': {
            'phone_number': phone_number,
            'phone_number_verified': True,
        }})
    phone_tokens_collection.delete_many({'helper_id': helper_id})

    return status('ok')


def trigger_phone_verification(email):
    # this function can be used for the initial send as well as resending

    helper_account = helper_accounts_collection.find_one({'email': email}, {'_id': 1})

    # Generate new token
    token = tokening.generate_random_key(length=5, numeric=True)
    helper_id = ObjectId(helper_account["_id"])

    # Create new token record
    record = {
        'helper_id': helper_id,
        'token': token,
        'timestamp_issued': datetime.now(),
    }
    operations = [
        DeleteMany({'helper_id': helper_id}),
        InsertOne(record)
    ]
    phone_tokens_collection.bulk_write(operations, ordered=True)

    # Trigger token-email
    return status('ok', token=token)


def confirm_phone_verification(email):
    # this function can be used for the initial send as well as resending
    helper_account = helper_accounts_collection.find_one({'email': email}, {'_id': 1})
    helper_id = ObjectId(helper_account["_id"])

    helper_accounts_collection.update_one(
        {'_id': helper_id},
        {'$set': {
            'phone_number_confirmed': True
        }}
    )

    return fetching.get_all_helper_data(email)


if __name__ == '__main__':
    # trigger_email_verification('1402', TEST_EMAIL)
    # email_tokens_collection.delete_many({})

    # confirm_email('iu694Wfs8p7zVggbWeuLIPXplEhQoMHMXeDriOhMl0WRfSQSGhgDzLC0BIsJm32s')

    print(trigger_phone_number_verification('5e8a66bddda9d4c16f9ad9e5'))
