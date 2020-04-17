
from flask_backend.database_scripts.call_scripts import call_scripts
from flask_backend.support_functions import routing, tokening, validating, formatting

from flask_restful import Resource
from flask import request
import os


class RESTCall(Resource):
    # IMPORTANT: For all of the following operations (except creating accounts) a
    # valid email/api_key pair must be provided! Otherwise private data might
    # leak to non-authorized entities

    def get(self):
        # Get all infos for a specific account
        params_dict = routing.get_params_dict(request)

        authentication_result = tokening.check_helper_api_key(
            params_dict, new_api_key=(os.getenv("ENVIRONMENT") == "production"))
        if authentication_result["status"] != "ok":
            return formatting.postprocess_response(authentication_result)

        result_dict = call_scripts.get_calls(params_dict['email'])
        return formatting.postprocess_response(result_dict, new_api_key=authentication_result["api_key"])

    def post(self):
        # Accept call

        params_dict = routing.get_params_dict(request, print_out=True)

        authentication_result = tokening.check_helper_api_key(params_dict)
        if authentication_result["status"] != "ok":
            return formatting.postprocess_response(authentication_result)

        validation_result = validating.validate_filter(params_dict)
        if validation_result["status"] != "ok":
            return formatting.postprocess_response(validation_result)

        result_dict = call_scripts.accept_call(params_dict)
        return formatting.postprocess_response(result_dict)

    def put(self):

        # Modify an accepted call (reject, fulfill, comment)

        params_dict = routing.get_params_dict(request, print_out=True)

        authentication_result = tokening.check_helper_api_key(params_dict)
        if authentication_result["status"] != "ok":
            return formatting.postprocess_response(authentication_result)

        validation_result = validating.validate_edit_call(params_dict)
        if validation_result["status"] != "ok":
            return formatting.postprocess_response(validation_result)

        result_dict = call_scripts.modify_call(params_dict)
        return formatting.postprocess_response(result_dict)
