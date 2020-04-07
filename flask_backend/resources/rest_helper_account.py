from flask_restful import Resource
from flask_backend.routes import support_functions as support_functions_rest

from flask import request
from flask_backend import status

from flask_backend.nosql_scripts import helper_account_scripts
from flask_backend.nosql_scripts.helper_account_scripts import api_authentication, support_functions



class RESTAccount(Resource):
    # IMPORTANT: For all of the following operations (except creating accounts) a
    # valid email/api_key pair must be provided! Otherwise private data might
    # leak to non-authorized entities

    def get(self):
        # Get all infos for a specific account
        params_dict = support_functions_rest.get_params_dict(request)

        print("lololo")
        print(params_dict)

        if api_authentication.helper_login_api_key(params_dict["email"], params_dict["api_key"])["status"] != "ok":
            return {"status": "invalid request"}

        return support_functions.get_all_helper_data(params_dict["email"])


    def post(self):
        # Create a new account
        params_dict = support_functions_rest.get_params_dict(request, print_out=True)

        for key in ["email", "password", "zip_code", "country"]:
            if key not in params_dict:
                return status(f"{key} is missing")

        add_response = helper_account_scripts.add_helper_account(params_dict["email"], params_dict["password"],
                                                                 params_dict["zip_code"], params_dict["country"])

        # 'add_helper_account' also takes care of the immediate login
        return add_response


    def put(self):
        # Modify an existing account
        params_dict = support_functions_rest.get_params_dict(request, print_out=True)

        if api_authentication.helper_login_api_key(params_dict["email"], params_dict["api_key"])["status"] != "ok":
            return {"status": "invalid request"}

        modify_response = helper_account_scripts.modify_helper_account(**params_dict)

        return modify_response


    # no delete method yet
