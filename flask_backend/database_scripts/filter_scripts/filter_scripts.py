
from flask_backend import helper_accounts_collection
from flask_backend.support_functions import formatting


def modify_filters(params_dict):

    if any([(key not in params_dict) for key in
           ['filter_type_local', 'filter_type_global', 'filter_language_german', 'filter_language_english']]):
        return "filters missing"

    if (params_dict['filter_type_local'] and params_dict['filter_type_global']):
        return "filters invalid"

    helper_accounts_collection.update_one(
        {'email': params_dict["email"]},
        {'$set': {
            'filter_type_local': params_dict['filter_type_local'],
            'filter_type_global': params_dict['filter_type_global'],
            'filter_language_german': params_dict['filter_language_german'],
            'filter_language_english': params_dict['filter_language_english'],
        }}
    )

    return formatting.status("ok")


def get_filters(email, new_api_key):

    helper_account = helper_accounts_collection.find_one({'email': email})

    if helper_account is None:
        return formatting.status("server error - missing helper record after successful authentication")

    filters = {
        "filter_type_local": helper_account['filter_type_local'],
        "filter_type_global": helper_account['filter_type_global'],
        "filter_language_german": helper_account['filter_language_german'],
        "filter_language_english": helper_account['filter_language_english']
    }

    return formatting.status("ok", new_api_key=new_api_key, filters=filters)
