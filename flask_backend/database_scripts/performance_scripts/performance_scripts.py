
from flask_backend import helper_accounts_collection, caller_accounts_collection, calls_collection
from flask_backend.support_functions import fetching


def get_performance(zip_code):
    adjacent_zip_codes = fetching.get_adjacent_zip_codes(zip_code)

    local_filter_dict = {
        'zip_code': {'$in': adjacent_zip_codes}
    }

    calls_filter_dict = {
        'call_type': {"$elemMatch": {"$eq": 'local'}},
        'zip_code': {'$in': adjacent_zip_codes},
        'status': 'fulfilled',
    }

    return {
        'performance': {
            'helpers': int(helper_accounts_collection.count_documents(local_filter_dict)),
            'callers': int(caller_accounts_collection.count_documents(local_filter_dict)),
            'calls': int(calls_collection.count_documents(calls_filter_dict)),
        }
    }
