
from flask_backend.database_scripts.filter_scripts import filter_scripts
from flask_backend.support_functions import routing, tokening

from flask_restful import Resource
from flask import request


class RESTFilter(Resource):

    def get(self):
        params_dict = routing.get_params_dict(request, print_out=True)

        authentication_result = tokening.check_helper_api_key(params_dict, new_api_key=True)
        if authentication_result["status"] != "ok":
            return authentication_result

        return filter_scripts.get_filters(params_dict['email'], authentication_result['api_key'])


    def put(self):
        params_dict = routing.get_params_dict(request, print_out=True)

        authentication_result = tokening.check_helper_api_key(params_dict)
        if authentication_result["status"] != "ok":
            return authentication_result

        return filter_scripts.modify_filters(params_dict)
