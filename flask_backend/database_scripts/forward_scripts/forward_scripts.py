
from flask_backend import helper_accounts_collection
from flask_backend.support_functions import formatting


def get_forward(email, new_api_key):

    helper_account = helper_accounts_collection.find_one({'email': email})

    if helper_account is None:
        return formatting.status("server error - missing helper record after successful authentication")

    return formatting.status("ok", new_api_key=new_api_key, forward=helper_account['forward'])


def modify_forward(params_dict):

    # Sequential if-statements because the latter
    # ones depend on the previous ones to be true

    for key in ['online', 'schedule_active', 'schedule']:
        if key not in params_dict:
            return formatting.status("filters missing")

    if type(params_dict['online']) != bool or type(params_dict['schedule_active']) != bool:
        return formatting.status("filters invalid")

    if type(params_dict['schedule']) != list:
        return formatting.status("filters invalid")

    for schedule_record in params_dict['schedule']:

        if type(schedule_record) != dict:
            return formatting.status("filters invalid")
        if len(schedule_record) != 2:
            return formatting.status("filters invalid")
        if ('from' not in schedule_record) or ('to' not in schedule_record):
            return formatting.status("filters invalid")
        if (type(schedule_record['from']) != int) or (type(schedule_record['to']) != int):
            return formatting.status("filters invalid")

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
