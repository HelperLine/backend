
from flask_backend import helper_accounts_collection
from flask_backend.support_functions import formatting

from datetime import datetime, timezone, timedelta


def get_forward(email, new_api_key):

    helper_account = helper_accounts_collection.find_one({'email': email})

    if helper_account is None:
        return formatting.status("server error - missing helper record after successful authentication")

    return formatting.status("ok", new_api_key=new_api_key, forward=helper_account['forward'])


def modify_forward(params_dict):

    # params_dict["forward"] has already been validated

    if params_dict["forward"]["online"]:
        params_dict["forward"].update({'last_switched_online': datetime.now(timezone(timedelta(hours=2)))})

    helper_accounts_collection.update_one(
        {'email': params_dict["email"]},
        {'$set': {
            'forward': params_dict["forward"]
        }}
    )

    return formatting.status("ok")
