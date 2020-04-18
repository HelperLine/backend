
from flask_backend import helper_accounts_collection, phone_tokens_collection
from flask_backend.support_functions import tokening, formatting, timing


def trigger(email):

    phone_tokens_collection.delete_many({
        '$or': [
            {'$and': [
                {'timestamp_issued': {'$lt': timing.get_current_time(offset_minutes=-3)}},
                {'phone_number': ''},
            ]},
            {'email': email}
        ]
    })

    # Generate new token
    # By including the existing tokens a duplicate token error is impossible,
    # however the token generation might take longer and is non-deterministic
    existing_tokens = [document['token'] for document in list(phone_tokens_collection.find({}, {'_id': 0, 'token': 1}))]
    token = tokening.generate_random_key(length=5, numeric=True, existing_tokens=existing_tokens)

    # Create new token record
    new_record = {
        'email': email,
        'token': token,
        'timestamp_issued': timing.get_current_time(),
        'phone_number': '',
    }
    phone_tokens_collection.insert_one(new_record)

    # Trigger token-email
    return formatting.status('ok', token=token)


def verify(token, phone_number):
    record = phone_tokens_collection.find_one({
        'token': token,
        'timestamp_issued': {'$gt': timing.get_current_time(offset_minutes=-3)},
    })

    if record is None:
        return formatting.status('token invalid'), 400

    phone_tokens_collection.update_one(
        {'token': token},
        {'$set': {'phone_number': phone_number}}
    )

    return formatting.status('ok'), 200


def fetch(email):
    record = phone_tokens_collection.find_one({'email': email}, {'_id': 0, 'phone_number': 1})

    if record is None:
        return formatting.status('not verification found'), 400

    if record['phone_number'] == '':
        return formatting.status('not verification found'), 400

    return formatting.status('ok', phone_number=record['phone_number']), 200


def confirm(email):
    # this function can be used for the initial send as well as resending

    record = phone_tokens_collection.find_one({'email': email}, {'_id': 0, 'phone_number': 1})

    if record is None:
        return formatting.status('not verification found'), 400

    if record['phone_number'] == '':
        return formatting.status('not verification found'), 400

    helper_accounts_collection.update_one(
        {'email': email},
        {'$set': {
            'phone_number': record['phone_number'],
            'phone_number_verified': True
        }}
    )
    phone_tokens_collection.delete_many({'email': email})

    return formatting.status("ok"), 200


if __name__ == '__main__':
    # trigger_email_verification('1402', TEST_EMAIL)
    # email_tokens_collection.delete_many({})

    # confirm_email('iu694Wfs8p7zVggbWeuLIPXplEhQoMHMXeDriOhMl0WRfSQSGhgDzLC0BIsJm32s')

    pass
