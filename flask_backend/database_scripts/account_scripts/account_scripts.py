from flask_backend import helper_accounts_collection, email_tokens_collection, helper_api_keys_collection
from flask_backend.database_scripts.verification_scripts import email_verification
from flask_backend.database_scripts.authentication_scripts import helper_authentication
from flask_backend.support_functions import tokening, formatting

from pymongo.errors import DuplicateKeyError
import datetime
import time
from datetime import timezone, timedelta


def get_account(email):
    helper_account = helper_accounts_collection.find_one({'email': email}, {'account.hashed_password': 0})

    if helper_account is None:
        return formatting.server_error_helper_record

    return formatting.status("ok", account=helper_account['account'])


def create_account(params_dict):

    email = params_dict["account"]["email"]
    password = params_dict["account"]["password"]
    zip_code = params_dict["account"]["zip_code"]
    country = params_dict["account"]["country"]

    current_timestamp = datetime.datetime.now(timezone(timedelta(hours=2)))
    new_helper = {
        'email': email,

        'account': {
            'register_date': current_timestamp.strftime('%d.%m.%y'),
            'email_verified': False,

            'phone_number': '',
            'phone_number_verified': False,

            'hashed_password': tokening.hash_password(password),
            'zip_code': zip_code,
            'country': country,
        },

        'filter': {
            'type': {
                'only_local': False,
                'only_global': False,
            },
            'language': {
                'german': False,
                'english': False,
            },
        },

        'forward': {
            'online': False,
            'last_switched_online': current_timestamp,
            'stay_online_after_call': False,
            'schedule_active': False,
            'schedule': []
        }
    }

    try:
        # inserting helper document
        helper_id = helper_accounts_collection.insert_one(new_helper).inserted_id
    except DuplicateKeyError as e:
        # If two people sign up exactla at once
        # (verfication done but inserting fails for one)
        print(f'DuplicateKeyError: {e}')
        return formatting.status('email already taken')

    # Send verification email and add verification record
    email_verification.trigger(email)

    # login and return email/api_key dict
    return helper_authentication.helper_login_password(email, password)


def modify_account(params_dict):
    existing_document = helper_accounts_collection.find_one({'email': params_dict["email"]})
    existing_account = existing_document["account"]
    new_account = params_dict["account"]

    update_dict = {}

    if 'new_email' in new_account:
        if (existing_document["email"] != new_account["new_email"]):
            if (existing_account['email_verified']):
                return formatting.status('email already verified')
            else:
                update_dict.update({"email": new_account["new_email"]})

    if 'old_password' in new_account and 'new_password' in new_account:
        if tokening.check_password(new_account['old_password'], existing_account['hashed_password']):
            update_dict.update({"account.hashed_password": tokening.hash_password(new_account['new_password'])})
        else:
            return formatting.status('old_password invalid')

    if 'zip_code' in new_account:
        update_dict.update({"account.zip_code": new_account['zip_code']})

    if 'country' in new_account:
        update_dict.update({"account.country": new_account['country']})

    if len(update_dict) != 0:
        helper_accounts_collection.update_one(
            {'email': existing_document["email"]},
            {'$set': update_dict}
        )

        if "email" in update_dict:
            # Send new verification email if new email valid
            email_tokens_collection.delete_many({'email': existing_document["email"]})
            helper_api_keys_collection.update_one({'email': existing_document["email"]},
                                                  {'$set': {'email': update_dict["email"]}})
            email_verification.trigger(update_dict["email"])

    return formatting.status("ok")


if __name__ == '__main__':
    t1 = time.time()
    # print(add_helper_account(TEST_EMAIL, TEST_PASSWORD, TEST_ZIP_CODE))
    t2 = time.time()

    print(f'total: {t2 - t1} seconds')
    helper_accounts_collection.delete_many({})
