
from flask_backend import helper_accounts_collection
from flask_backend.support_functions import formatting, timing


def get_forward(email):

    helper_account = helper_accounts_collection.find_one({'email': email})

    if helper_account is None:
        return formatting.status("server error - missing helper record after successful authentication")

    return formatting.status("ok", forward=helper_account['forward'])


def modify_forward(params_dict):

    # params_dict["forward"] has already been validated

    params_dict["forward"].update({'last_modified': timing.get_current_time()})

    helper_accounts_collection.update_one(
        {'email': params_dict["email"]},
        {'$set': {
            'forward': params_dict["forward"]
        }}
    )

    return formatting.status("ok")
