
from flask_backend.database_scripts.settings_scripts import forward_scripts
from flask_backend.support_functions import routing, tokening, validating

from flask_restful import Resource
from flask import request


class RESTForward(Resource):

    def get(self):
        params_dict = routing.get_params_dict(request, print_out=True)

        authentication_result = tokening.check_helper_api_key(params_dict, new_api_key=True)
        if authentication_result["status"] != "ok":
            return authentication_result

        return forward_scripts.get_forward(params_dict['email'], authentication_result['api_key'])


    def put(self):
        params_dict = routing.get_params_dict(request, print_out=True)

        authentication_result = tokening.check_helper_api_key(params_dict)
        if authentication_result["status"] != "ok":
            return authentication_result

        validation_result = validating.validate_forward(params_dict)
        if validation_result["status"] != "ok":
            return validation_result

        return forward_scripts.modify_forward(params_dict)

