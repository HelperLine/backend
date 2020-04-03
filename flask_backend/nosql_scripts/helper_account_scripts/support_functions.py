
from flask_backend import bcrypt, BCRYPT_SALT, status, helper_accounts_collection, calls_collection
import random


def generate_random_key(length=32):
    possible_characters = []

    # Characters '0' through '9'
    possible_characters += [chr(x) for x in range(48, 58)]

    # Characters 'A' through 'Z'
    possible_characters += [chr(x) for x in range(65, 91)]

    # Characters 'a' through 'z'
    possible_characters += [chr(x) for x in range(97, 123)]

    random_key = ""

    for i in range(length):
        random_key += random.choice(possible_characters)

    return random_key


def hash_password(password):
    return bcrypt.generate_password_hash(password + BCRYPT_SALT).decode('UTF-8')


def check_password(password, hashed_password):
    return bcrypt.check_password_hash(hashed_password, password + BCRYPT_SALT)


def get_all_helper_data(email):
    helper_account = helper_accounts_collection.find_one({"email": email})

    account_dict = {
        "email_verified": helper_account["email_verified"],
        "zip_code": helper_account["zip_code"],
        "country": helper_account["country"],
    }

    # TODO: !
    calls_dict = get_helper_calls_dict(helper_account["_id"])

    # TODO: !
    performance_dict = {
        "area": {
            "volunteers": 1,
            "callers": 0,
            "calls": 0,
        },
        "account": {
            "registered": helper_account["register_date"],
            "calls": len(calls_dict["fulfilled"]),
        }
    }

    filters_dict = {
        "type": {
            "local": helper_account["filter_type_local"],
            "global": helper_account["filter_type_global"],
        },
        "language": {
            "german": helper_account["filter_language_german"],
            "english": helper_account["filter_language_english"],
        },
    }

    return status("ok",
                  email=email,
                  account=account_dict,
                  calls=calls_dict,
                  performance=performance_dict,
                  filters=filters_dict)


def get_helper_calls_dict(helper_id):
    # every_call should have the field:
    # call_id, caller_id, phone_number, local, zip_code, status
    # timestamp_received, timestamp_accepted, (timestamp_fulfilled)

    return {
        "accepted": list(calls_collection.find({"helper_id": helper_id, "status": "accepted"})),
        "fulfilled": list(calls_collection.find({"helper_id": helper_id, "status": "fulfilled"})),
    }
