
from flask_backend import helper_accounts_collection
from flask_backend.support_functions import formatting


def get_forward(email, new_api_key):

    helper_account = helper_accounts_collection.find_one({'email': email})

    if helper_account is None:
        return formatting.status("server error - missing helper record after successful authentication")

    return formatting.status("ok", new_api_key=new_api_key, forward=helper_account['forward'])


def modify_forward(params_dict):

    if any([(key not in params_dict) for key in ['online', 'schedule_active', 'schedule']]):
        return "forward missing"

    helper_accounts_collection.update_one(
        {'email': params_dict["email"]},
        {'$set': {
            'forward': {
                'online': params_dict['online'],
                'schedule_active': params_dict['schedule_active'],
                'schedule': params_dict['schedule'],
            }
        }}
    )

    return formatting.status("ok")
