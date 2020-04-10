
from flask_backend import app, status, helper_accounts_collection, api
from flask_backend.database_scripts.helper_scripts import api_authentication
from flask_backend.database_scripts.call_scripts import dequeue, forwarding
from flask_backend.support_functions import routing, fetching

from flask import request


from flask_backend.restful_resources.rest_call import RESTCall
api.add_resource(RESTCall, '/backend/v1/database/call')


@app.route('/backend/<api_version>/calls/accept', methods=['POST'])
def route_call_accept(api_version):

    if api_version == "v1":
        params_dict = routing.get_params_dict(request, print_out=True)

        if api_authentication.helper_login_api_key(params_dict['email'], params_dict['api_key'])['status'] != 'ok':
            return status('invalid email/api_key')

        helper = helper_accounts_collection.find_one({'email': params_dict['email']})

        if helper is None:
            return status('server error: helper record not found')

        if 'filter_type_local' not in params_dict or 'filter_type_global' not in params_dict or \
                'filter_language_german' not in params_dict or 'filter_language_english' not in params_dict:
            return status('filter parameters missing')

        dequeue_result = dequeue.dequeue(
            str(helper['_id']),
            zip_code=helper['zip_code'],
            only_local_calls=params_dict['filter_type_local'],
            only_global_calls=params_dict['filter_type_global'],
            accept_german=params_dict['filter_language_german'],
            accept_english=params_dict['filter_language_english']
        )

        if dequeue_result['status'] != 'ok':
            return dequeue_result
        else:
            return_result = fetching.get_all_helper_data(helper_id=str(helper['_id']))
            print(return_result)
            return return_result

    else:
        return status("api_version invalid")


@app.route('/backend/<api_version>/forward/online', methods=['PUT'])
def route_call_set_online(api_version):

    if api_version == "v1":
        params_dict = routing.get_params_dict(request, print_out=True)

        if api_authentication.helper_login_api_key(params_dict['email'], params_dict['api_key'])['status'] != 'ok':
            return status('invalid email/api_key')

        helper = helper_accounts_collection.find_one({'email': params_dict['email']})

        if helper is None:
            return status('server error: helper record not found')

        if 'filter_type_local' not in params_dict or 'filter_type_global' not in params_dict or \
                'filter_language_german' not in params_dict or 'filter_language_english' not in params_dict:
            return status('filter parameters missing')

        return forwarding.set_online(
            str(helper["_id"]),
            filter_type_local=params_dict["filter_type_local"],
            filter_type_global=params_dict["filter_type_global"],
            filter_language_german=params_dict["filter_language_german"],
            filter_language_english=params_dict["filter_language_english"],
        )

    else:
        return status("api_version invalid")


@app.route('/backend/<api_version>/forward/offline', methods=['PUT'])
def route_call_set_offline(api_version):

    if api_version == "v1":
        params_dict = routing.get_params_dict(request, print_out=True)

        if api_authentication.helper_login_api_key(params_dict['email'], params_dict['api_key'])['status'] != 'ok':
            return status('invalid email/api_key')

        helper = helper_accounts_collection.find_one({'email': params_dict['email']})

        if helper is None:
            return status('server error: helper record not found')

        return forwarding.set_offline(str(helper["_id"]))

    else:
        return status("api_version invalid")
