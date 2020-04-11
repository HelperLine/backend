
from flask_backend.database_scripts.helper_scripts import helper_scripts
from flask_backend.support_functions import routing, fetching, tokening

from flask_restful import Resource
from flask import request


class RESTHelper(Resource):
    # IMPORTANT: For all of the following operations (except creating accounts) a
    # valid email/api_key pair must be provided! Otherwise private data might
    # leak to non-authorized entities

    def get(self):
        # Get all infos for a specific account
        params_dict = routing.get_params_dict(request)

        authentication_result = tokening.check_helper_api_key(params_dict)
        if authentication_result["status"] != "ok":
            return authentication_result

        return fetching.get_all_helper_data(params_dict['email'])


    def post(self):
        # Create a new account
        return helper_scripts.add_helper_account(routing.get_params_dict(request))


    def put(self):
        # Modify an existing account
        params_dict = routing.get_params_dict(request)

        authentication_result = tokening.check_helper_api_key(params_dict)
        if authentication_result["status"] != "ok":
            return authentication_result

        return helper_scripts.modify_helper_account(params_dict)
