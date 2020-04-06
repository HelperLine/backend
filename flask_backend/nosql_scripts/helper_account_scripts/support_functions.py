
from flask_backend import bcrypt, BCRYPT_SALT, status, helper_accounts_collection, caller_accounts_collection, calls_collection, zip_codes_collection
import random


def generate_random_key(length=32, numeric=False):
    possible_characters = []

    # Characters '0' through '9'
    possible_characters += [chr(x) for x in range(48, 58)]

    if not numeric:
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

    print(helper_account)

    account_dict = {
        "email_verified": helper_account["email_verified"],

        "phone_number": helper_account["phone_number"],
        "phone_number_verified": helper_account["phone_number_verified"],
        "phone_number_confirmed": helper_account["phone_number_confirmed"],

        "zip_code": helper_account["zip_code"],
        "country": helper_account["country"],
    }

    filters_dict = get_helper_filters_dict(helper_account)


    # TODO: !
    calls_dict = get_helper_calls_dict(helper_account["_id"])

    # TODO: !
    performance_dict = get_helper_performance_dict(helper_account, calls_dict)

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

def get_helper_filters_dict(helper_account):
    return {
        "type": {
            "local": helper_account["filter_type_local"],
            "global": helper_account["filter_type_global"],
        },
        "language": {
            "german": helper_account["filter_language_german"],
            "english": helper_account["filter_language_english"],
        },
    }


def get_helper_performance_dict(helper_account, calls_dict):
    adjacent_zip_codes = get_adjacent_zip_codes(helper_account["zip_code"])

    return {
        "area": {
            "volunteers": int(helper_accounts_collection.count_documents({"zip_code": {"$in": adjacent_zip_codes}})),
            "callers": int(caller_accounts_collection.count_documents({"zip_code": {"$in": adjacent_zip_codes}})),
            "calls": 0,
        },
        "account": {
            "registered": helper_account["register_date"],
            "calls": len(calls_dict["fulfilled"]),
        }
    }


def get_adjacent_zip_codes(zip_code):
    # The returned list should include
    #  * all zip codes in a radius of 5km (at most 20 zip codes)
    #  * at least 8 zip codes (some may be more than 5km away)

    raw_adjacency_list = zip_codes_collection.find_one({"zip_code": zip_code}, {"_id": 0, "adjacent_zip_codes": 1})

    if raw_adjacency_list is None:
        return [zip_code]

    zip_codes = [(record["zip_code"], record["distance"]) for record in raw_adjacency_list["adjacent_zip_codes"]]

    if len(zip_codes) <= 8:
        return [record[0] for record in zip_code] + [zip_code]

    zip_codes.sort(key=lambda x: x[1])

    # Take at least 8 zip codes
    zip_code_final = zip_codes[0:8]
    zip_codes = zip_codes[8:]

    # Add all the remaining zip codes closer than 5km
    zip_codes = list(filter(lambda x: x[1] < 5, zip_codes))
    zip_code_final += zip_codes

    return [record[0] for record in zip_code_final] + [zip_code]


if __name__ == "__main__":
    print(get_all_helper_data("makowskimoritz@gmail.com"))


