
from flask_backend.database_scripts.settings_scripts import forward_scripts
from flask_backend.support_functions import routing, tokening, validating, formatting

from flask_restful import Resource
from flask import request
import os


class RESTForward(Resource):

    def get(self):
        params_dict = routing.get_params_dict(request, print_out=True)

        authentication_result = tokening.check_helper_api_key(
            params_dict, new_api_key=(os.getenv("ENVIRONMENT") == "production"))
        if authentication_result["status"] != "ok":
            return formatting.postprocess_response(authentication_result)

        result_dict = forward_scripts.get_forward(params_dict['email'])
        return formatting.postprocess_response(result_dict, new_api_key=authentication_result["api_key"])


    def put(self):
        params_dict = routing.get_params_dict(request, print_out=True)

        authentication_result = tokening.check_helper_api_key(params_dict)
        if authentication_result["status"] != "ok":
            return formatting.postprocess_response(authentication_result)

        validation_result = validating.validate_forward(params_dict)
        if validation_result["status"] != "ok":
            return formatting.postprocess_response(validation_result)

        result_dict = forward_scripts.modify_forward(params_dict)
        return formatting.postprocess_response(result_dict)

