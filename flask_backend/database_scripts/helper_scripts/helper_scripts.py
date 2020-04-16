from flask_backend import helper_accounts_collection, email_tokens_collection
from flask_backend.database_scripts.helper_scripts import email_verification, verify_register_form, api_authentication
from flask_backend.support_functions import tokening, verifying, formatting

from pymongo.errors import DuplicateKeyError
import datetime
import time
from datetime import timezone, timedelta


def get_account(email, new_api_key):
    helper_account = helper_accounts_collection.find_one({'email': email})

    if helper_account is None:
        return formatting.status("server error - missing helper record after successful authentication")

    return formatting.status("ok", new_api_key=new_api_key, account=helper_account['account'])


def create_account(params_dict):
    if 'account' not in params_dict:
        return formatting.status("account missing")

    for key in ['email', 'password', 'zip_code', 'country']:
        if key not in params_dict['account']:
            return formatting.status(f'{key} missing')

    email = params_dict["account"]["email"]
    password = params_dict["account"]["password"]
    zip_code = params_dict["account"]["zip_code"]
    country = params_dict["account"]["country"]

    verification_status = verify_register_form.verify_register_form(email, password, zip_code, country)

    if verification_status['status'] == 'ok':

        current_timestamp = datetime.datetime.now(timezone(timedelta(hours=2)))
        new_helper = {
            'email': email,

            'account': {
                'register_date': current_timestamp.strftime('%d.%m.%y'),
                'email_verified': False,

                'phone_number': '',
                'phone_number_verified': False,  # Verfication from our side (Call and enter confirmation code)
                'phone_number_confirmed': False,  # Confirmation from the volunteer ('Is this your phone number?')

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
                    'accept_german': False,
                    'accept_english': False,
                },
            },

            'forward': {
                'online': False,
                'last_switched_online': current_timestamp,

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
        email_verification.trigger_email_verification(email)

        # login and return email/api_key dict
        return api_authentication.helper_login_password(email, password)

    else:
        return verification_status


def modify_account(params_dict):
    existing_document = helper_accounts_collection.find_one({'email': params_dict["email"]})
    existing_account = existing_document["account"]
    new_account = params_dict["account"]

    # Strategy: Modify new_account to be the update_dict for the helper account
    # All keys not in new_account remain unchanged

    new_email = existing_document["email"]

    if 'email' in new_account:
        if (existing_document["email"] != new_account["email"]):
            if (existing_account['email_verified']):
                return formatting.status('email already verified')
            else:
                if not verifying.verify_email_format(new_account['email']):
                    return formatting.status('email format invalid')

            # Send new verification email if new email valid
            email_tokens_collection.delete_one({'email': existing_document["email"]})
            email_verification.trigger_email_verification(new_account["email"])
            new_email = new_account["email"]

    # this does not raise errors if the key does not exist
    new_account.pop('email', None)

    if 'old_password' in new_account and 'new_password' in new_account:
        if tokening.check_password(new_account['old_password'], existing_account['hashed_password']):
            if not verifying.verify_password_format(new_account['new_password']):
                return formatting.status('new_password format invalid')
            new_account.update({
                "hashed_password": tokening.hash_password(new_account['new_password'])
            })
        else:
            return formatting.status('old_password invalid')

    # these do not raise errors if any of these keys does not exist
    new_account.pop('old_password', None)
    new_account.pop('new_password', None)

    if 'zip_code' in new_account:
        if not verifying.verify_zip_code_format(new_account['zip_code']):
            return formatting.status('zip_code format invalid')

    if 'country' in new_account:
        if not verifying.verify_country_format(params_dict['country']):
            return formatting.status('country invalid')

    if any([(key not in ["hashed_password", "zip_code", "country"]) for key in new_account]):
        return formatting.status("too many parameters")

    helper_accounts_collection.update_one(
        {'email': existing_account},
        {'$set': {
            'email': new_email,
            'account': new_account
        }}
    )

    return formatting.status("ok")


if __name__ == '__main__':
    t1 = time.time()
    # print(add_helper_account(TEST_EMAIL, TEST_PASSWORD, TEST_ZIP_CODE))
    t2 = time.time()

    print(f'total: {t2 - t1} seconds')
    helper_accounts_collection.delete_many({})
