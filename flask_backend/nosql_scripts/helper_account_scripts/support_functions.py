from flask_backend import bcrypt, BCRYPT_SALT, status, helper_accounts_collection, caller_accounts_collection, \
    calls_collection, zip_codes_collection
import random

from bson import ObjectId


def generate_random_key(length=32, numeric=False):
    possible_characters = []

    # Characters '0' through '9'
    possible_characters += [chr(x) for x in range(48, 58)]

    if not numeric:
        # Characters 'A' through 'Z'
        possible_characters += [chr(x) for x in range(65, 91)]

        # Characters 'a' through 'z'
        possible_characters += [chr(x) for x in range(97, 123)]

    random_key = ''

    for i in range(length):
        random_key += random.choice(possible_characters)

    return random_key


def hash_password(password):
    return bcrypt.generate_password_hash(password + BCRYPT_SALT).decode('UTF-8')


def check_password(password, hashed_password):
    return bcrypt.check_password_hash(hashed_password, password + BCRYPT_SALT)


def get_all_helper_data(email=None, helper_id=None):
    if email is not None:
        helper_account = helper_accounts_collection.find_one({'email': email})
    else:
        helper_account = helper_accounts_collection.find_one({'_id': ObjectId(helper_id)})

    if helper_account is None:
        return status('invalid email/helper_id')

    account_dict = {
        'email_verified': helper_account['email_verified'],

        'phone_number': helper_account['phone_number'],
        'phone_number_verified': helper_account['phone_number_verified'],
        'phone_number_confirmed': helper_account['phone_number_confirmed'],

        'zip_code': helper_account['zip_code'],
        'country': helper_account['country'],
    }

    filters_dict = get_helper_filters_dict(helper_account)

    # TODO: !
    calls_dict = get_helper_calls_dict(helper_account['_id'])

    # TODO: !
    performance_dict = get_helper_performance_dict(helper_account, calls_dict)

    return status('ok',
                  email=email,
                  account=account_dict,
                  calls=calls_dict,
                  performance=performance_dict,
                  filters=filters_dict)


def get_helper_calls_dict(helper_id):
    # every_call should have the field:
    # call_id, caller_id, phone_number, local, zip_code, status
    # timestamp_received, timestamp_accepted, (timestamp_fulfilled)

    match_dict = {
        'helper_id': ObjectId(helper_id),
    }

    lookup_dict = {
            'from': 'caller_accounts',
            'localField': 'caller_id',
            'foreignField': '_id',
            'as': 'caller'
    }

    project_dict = {
        '_id': 1,
        'status': 1,

        'timestamp_received': 1,
        'timestamp_accepted': 1,
        'timestamp_fulfilled': 1,

        'comment': 1,

        'caller': {
            'phone_number': 1
        }
    }


    raw_list = list(
        calls_collection.aggregate([
            {'$match': match_dict},
            {'$lookup': lookup_dict},
            {'$project': project_dict},
        ]))

    projected_list = [{
        'call_id': str(call['_id']),
        'status': call['status'],
        'timestamp_received': call['timestamp_received'],
        'timestamp_accepted': call['timestamp_accepted'],
        'timestamp_fulfilled': call['timestamp_fulfilled'],
        'comment': call['comment'],
        'phone_number': call['caller'][0]['phone_number']
    } for call in raw_list]

    return {
        'accepted': list(filter(lambda x: x['status'] == 'accepted', projected_list)),
        'fulfilled': list(filter(lambda x: x['status'] == 'fulfilled', projected_list)),
    }


def get_helper_filters_dict(helper_account):
    return {
        'type': {
            'local': helper_account['filter_type_local'],
            'global': helper_account['filter_type_global'],
        },
        'language': {
            'german': helper_account['filter_language_german'],
            'english': helper_account['filter_language_english'],
        },
    }


def get_helper_performance_dict(helper_account, calls_dict):
    adjacent_zip_codes = get_adjacent_zip_codes(helper_account['zip_code'])

    return {
        'area': {
            'volunteers': int(helper_accounts_collection.count_documents({'zip_code': {'$in': adjacent_zip_codes}})),
            'callers': int(caller_accounts_collection.count_documents({'zip_code': {'$in': adjacent_zip_codes}})),
            'calls': 0,
        },
        'account': {
            'registered': helper_account['register_date'],
            'calls': len(calls_dict['fulfilled']),
        }
    }


def get_adjacent_zip_codes(zip_code):
    # The returned list should include
    #  * all zip codes in a radius of 5km (at most 20 zip codes)
    #  * at least 8 zip codes (some may be more than 5km away)

    raw_adjacency_list = zip_codes_collection.find_one({'zip_code': zip_code}, {'_id': 0, 'adjacent_zip_codes': 1})

    if raw_adjacency_list is None:
        return [zip_code]

    zip_codes = [(record['zip_code'], record['distance']) for record in raw_adjacency_list['adjacent_zip_codes']]

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


if __name__ == '__main__':
    # print(get_all_helper_data('makowskimoritz@gmail.com'))

    # Testing: LOOKUP in NoSQL is the equvalent of a JOIN operation in SQL

    accepted_calls = list(
        calls_collection.aggregate([
            {
                '$match': {
                    'helper_id': ObjectId('5e8a839c2b60889bbec3ef7c'),
                    'status': 'accepted',
                }
            },
            {
                '$lookup': {
                        'from': 'caller_accounts',
                        'localField': 'caller_id',
                        'foreignField': '_id',
                        'as': 'caller'
                    }
            }, {
                '$project': {
                    '_id': 1,
                    'timestamp_received': 1,
                    'timestamp_accepted': 1,
                    'timestamp_fulfilled': 1,
                    'comment': 1,

                    'caller': {
                        'phone_number': 1
                    }
                }
            },
        ]))

    accepted_calls = [{
        'call_id': str(call['_id']),
        'timestamp_received': call['timestamp_received'],
        'timestamp_accepted': call['timestamp_accepted'],
        'comment': call['comment'],
        'phone_number': call['caller'][0]['phone_number']
    } for call in accepted_calls]

    print(accepted_calls)
