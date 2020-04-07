from flask_restful import Resource
from flask_backend.routes import support_functions as support_functions_rest

from flask import request
from flask_backend import status, calls_collection, helper_accounts_collection

from flask_backend.nosql_scripts import helper_account_scripts
from flask_backend.nosql_scripts.helper_account_scripts import api_authentication, support_functions

from flask_backend.nosql_scripts.call_scripts import fulfill_call, reject_call, comment_call

from bson import ObjectId


class RESTCall(Resource):
    # IMPORTANT: For all of the following operations (except creating accounts) a
    # valid email/api_key pair must be provided! Otherwise private data might
    # leak to non-authorized entities

    def put(self):
        # Modify an existing account
        params_dict = support_functions_rest.get_params_dict(request, print_out=True)

        if api_authentication.helper_login_api_key(params_dict['email'], params_dict['api_key'])['status'] != 'ok':
            return {'status': 'email/api_key invalid'}



        helper = helper_accounts_collection.find_one({"email": params_dict["email"]})

        if helper is None:
            return status("backend error")



        if 'call_id' not in params_dict:
            return status('call_id missing')

        call = calls_collection.find_one({"_id": ObjectId(params_dict["call_id"])})

        if call is None:
            return status("call_id invalid")



        if str(call["helper_id"]) != str(helper["_id"]):
            return status("not authorized to edit this call")



        if 'action' not in params_dict:
            return status('call_action missing')


        if params_dict["action"] in ["fulfill", "reject"] and call["status"] == "fulfilled":
            return status('cannot change a fulfilled call')


        if params_dict["action"] == "fulfill":
            fulfill_call(str(params_dict["call_id"]), str(call["helper_id"]))

        elif params_dict["action"] == "reject":
            reject_call(str(params_dict["call_id"]), str(call["helper_id"]))

        elif params_dict["action"] == "comment":
            if 'comment' not in params_dict:
                return status('comment missing')

            comment_call(str(params_dict["call_id"]), params_dict["comment"])
        else:
            return status('action invalid')

        return support_functions.get_all_helper_data(email=params_dict["email"])
