
from flask_backend.database_scripts.account_scripts import account_scripts
from flask_backend.support_functions import routing, tokening, validating, formatting

from flask_restful import Resource
from flask import request


class RESTAccount(Resource):
    # IMPORTANT: For all of the following operations (except creating accounts) a
    # valid email/api_key pair must be provided! Otherwise private data might
    # leak to non-authorized entities

    def get(self):
        # Get all infos for a specific account
        params_dict = routing.get_params_dict(request)

        authentication_result = tokening.check_helper_api_key(params_dict, new_api_key=True)
        if authentication_result["status"] != "ok":
            return formatting.postprocess_response(authentication_result)

        result_dict = account_scripts.get_account(params_dict['email'])
        return formatting.postprocess_response(result_dict, new_api_key=authentication_result["api_key"])


    def post(self):
        # Create a new account
        params_dict = routing.get_params_dict(request, print_out=True)

        validation_result = validating.validate_create_account(params_dict)
        if validation_result["status"] != "ok":
            return formatting.postprocess_response(validation_result)

        result_dict = account_scripts.create_account(params_dict)
        return formatting.postprocess_response(result_dict)


    def put(self):
        # Modify an existing account
        params_dict = routing.get_params_dict(request)

        authentication_result = tokening.check_helper_api_key(params_dict)
        if authentication_result["status"] != "ok":
            return formatting.postprocess_response(authentication_result)

        validation_result = validating.validate_edit_account(params_dict)
        if validation_result["status"] != "ok":
            return formatting.postprocess_response(validation_result)

        result_dict = account_scripts.modify_account(params_dict)
        return formatting.postprocess_response(result_dict)
