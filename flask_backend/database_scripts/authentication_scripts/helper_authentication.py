
from flask_backend import helper_api_keys_collection, helper_accounts_collection
from flask_backend.support_functions import tokening, fetching, formatting

from pymongo import DeleteMany, InsertOne


# ---------------------------------------------------------------------------------------------------------------------


def helper_create_new_api_key(email):
    api_key = tokening.generate_random_key(length=64)

    operations = [
        DeleteMany({'email': email}),
        InsertOne({'email': email, 'api_key': api_key})
    ]
    helper_api_keys_collection.bulk_write(operations, ordered=True)

    return api_key


def helper_delete_api_key(email):
    helper_api_keys_collection.delete_many({'email': email})


# ---------------------------------------------------------------------------------------------------------------------


def helper_login_password(email, password):
    helper_account = helper_accounts_collection.find_one({'email': email})

    if helper_account is not None:
        if tokening.check_password(password, helper_account['account']['hashed_password']):
            api_key = helper_create_new_api_key(email)
            return formatting.status("ok", email=email, api_key=api_key), 200

    return formatting.status('email/password invalid'), 401


def helper_login_api_key(email, api_key, new_api_key=False):
    helper_api_key = helper_api_keys_collection.find_one({'email': email})

    if helper_api_key is not None:
        if api_key == helper_api_key['api_key']:
            if new_api_key:
                api_key = helper_create_new_api_key(email)
            return formatting.status("ok", email=email, api_key=api_key), 200

    return formatting.status('email/api_key invalid'), 401


def helper_logout(email, api_key):
    helper_api_key = helper_api_keys_collection.find_one({'email': email})
    if api_key == helper_api_key['api_key']:
        helper_delete_api_key(email)
    return formatting.status('ok'), 200
