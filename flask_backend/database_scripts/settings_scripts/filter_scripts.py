
from flask_backend import helper_accounts_collection
from flask_backend.support_functions import formatting


def get_filter(email, new_api_key):

    helper_account = helper_accounts_collection.find_one({'email': email})

    if helper_account is None:
        return formatting.status("server error - missing helper record after successful authentication")

    return formatting.status("ok", new_api_key=new_api_key, filter=helper_account['filter'])


def modify_filter(params_dict):

    # params_dict["filter"] has already been validated

    helper_accounts_collection.update_one(
        {'email': params_dict["email"]},
        {'$set': {
            'filter': params_dict["filter"]
        }}
    )

    return formatting.status("ok")
