
from flask_backend import helper_accounts_collection, helper_api_keys_collection, email_tokens_collection
from flask_backend.database_scripts.helper_scripts import email_verification, verify_register_form, api_authentication
from flask_backend.support_functions import tokening, fetching, verifying, formatting

from pymongo.errors import DuplicateKeyError
import datetime
import time


def add_helper_account(params_dict):
    for key in ['email', 'password', 'zip_code', 'country']:
        if key not in params_dict:
            return formatting.status(f'{key} missing')

    email = params_dict["email"]
    password = params_dict["password"]
    zip_code = params_dict["zip_code"]
    country = params_dict["country"]

    verification_status = verify_register_form.verify_register_form(email, password, zip_code, country)

    if verification_status['status'] == 'ok':
        new_helper = {
            'email': email,
            'email_verified': False,

            'phone_number': '',
            'phone_number_verified': False,  # Verfication from our side (Call and enter confirmation code)
            'phone_number_confirmed': False,  # Confirmation from the volunteer ('Is this your phone number?')

            'hashed_password': tokening.hash_password(password),
            'zip_code': zip_code,
            'country': country,

            'register_date': datetime.datetime.now().strftime('%d.%m.%y'),

            'filter_type_local': False,
            'filter_type_global': False,
            'filter_language_german': False,
            'filter_language_english': False,

            'online': False,
            'last_switched_online': datetime.datetime.now(),
            'online_schedule': []
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


def modify_helper_account(params_dict):

    email = params_dict["email"]  # proven to exists after authentication

    helper_account = helper_accounts_collection.find_one({'email': email})

    new_filter_type_local = new_filter_type_global = None

    if 'filter_type_local' in params_dict and 'filter_type_global' in params_dict:
        if not (params_dict['filter_type_local'] and params_dict['filter_type_global']):
            new_filter_type_local = params_dict['filter_type_local']
            new_filter_type_global = params_dict['filter_type_global']

    if new_filter_type_local is None or new_filter_type_global is None:
        new_filter_type_local = helper_account['filter_type_local']
        new_filter_type_global = helper_account['filter_type_global']

    if 'filter_language_german' in params_dict:
        new_filter_language_german = params_dict['filter_language_german']
    else:
        new_filter_language_german = helper_account['filter_language_german']

    if 'filter_language_english' in params_dict:
        new_filter_language_english = params_dict['filter_language_english']
    else:
        new_filter_language_english = helper_account['filter_language_english']

    if 'new_email' in params_dict:
        if (email != params_dict['new_email']) and (helper_account['email_verified']):
            return formatting.status('email already verified')
        else:
            if not verifying.verify_email_format(params_dict['new_email']):
                return formatting.status('email format invalid')
            else:
                new_email = params_dict['new_email']
    else:
        new_email = email

    if 'old_password' in params_dict and 'new_password' in params_dict:
        if tokening.check_password(params_dict['old_password'], helper_account['hashed_password']):
            if not verifying.verify_password_format(params_dict['new_password']):
                return formatting.status('password format invalid')
            else:
                new_password = tokening.hash_password(params_dict['new_password'])
        else:
            return formatting.status('old_password invalid')
    else:
        new_password = helper_account['hashed_password']

    if 'zip_code' in params_dict:
        if not verifying.verify_zip_code_format(params_dict['zip_code']):
            return formatting.status('zip_code format invalid')
        else:
            new_zip_code = params_dict['zip_code']
    else:
        new_zip_code = helper_account['zip_code']

    if 'country' in params_dict:
        if not verifying.verify_country_format(params_dict['country']):
            return formatting.status('country invalid')
        else:
            new_country = params_dict['country']
    else:
        new_country = helper_account['country']

    if (new_email != helper_account['email']) or (new_password != helper_account['hashed_password']) or \
            (new_zip_code != helper_account['zip_code']) or (new_country != helper_account['country']) or \
            (new_filter_type_local != helper_account['filter_type_local']) or \
            (new_filter_type_global != helper_account['filter_type_global']) or \
            (new_filter_language_german != helper_account['filter_language_german']) or \
            (new_filter_language_english != helper_account['filter_language_english']):

        modified_helper_account = {
            'email': new_email,

            'hashed_password': new_password,
            'zip_code': new_zip_code,
            'country': new_country,

            'filter_type_local': new_filter_type_local,
            'filter_type_global': new_filter_type_global,
            'filter_language_german': new_filter_language_german,
            'filter_language_english': new_filter_language_english,
        }

        helper_accounts_collection.update_one({'email': email}, {'$set': modified_helper_account})

        if email != new_email:
            helper_api_keys_collection.update_one({'email': email}, {'$set': {'email': new_email}})
            email_tokens_collection.delete_one({'email': email})
            email_verification.trigger_email_verification(new_email)

        # api_key remains the same
        response_dict = fetching.get_all_helper_data(new_email)
    else:
        response_dict = fetching.get_all_helper_data(email)

    return response_dict



if __name__ == '__main__':
    t1 = time.time()
    # print(add_helper_account(TEST_EMAIL, TEST_PASSWORD, TEST_ZIP_CODE))
    t2 = time.time()

    print(f'total: {t2 - t1} seconds')
    helper_accounts_collection.delete_many({})
