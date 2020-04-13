
from flask_backend import calls_collection, helper_accounts_collection
from flask_backend.database_scripts.call_scripts import call_scripts
from flask_backend.support_functions import routing, fetching, tokening, formatting

from flask_restful import Resource
from flask import request
from bson import ObjectId


class RESTCall(Resource):
    # IMPORTANT: For all of the following operations (except creating accounts) a
    # valid email/api_key pair must be provided! Otherwise private data might
    # leak to non-authorized entities

    def put(self):

        # Modify an existing account
        params_dict = routing.get_params_dict(request, print_out=True)



        # Step 1) Authenticate

        authentication_result = tokening.check_helper_api_key(params_dict)
        if authentication_result["status"] != "ok":
            return authentication_result



        # Step 2) Check database correctness

        helper = helper_accounts_collection.find_one({"email": params_dict["email"]})
        if helper is None:
            return formatting.status("server error: helper record not found after successful authentication")

        if 'call_id' not in params_dict:
            return formatting.status('call_id missing')

        call = calls_collection.find_one({"_id": ObjectId(params_dict["call_id"])})

        if call is None:
            return formatting.status("call_id invalid")



        # Step 3) Check eligibility to modify this call

        if 'action' not in params_dict:
            return formatting.status('action missing')

        if str(call["helper_id"]) != str(helper["_id"]):
            return formatting.status("not authorized to edit this call")

        if (call["status"] == "fulfilled") and (params_dict["action"] in ["reject", "fulfill"]):
            return formatting.status('cannot change a fulfilled call')



        # Step 4) Execute action if possible

        if params_dict["action"] == "fulfill":
            call_scripts.fulfill_call(params_dict["call_id"], helper["_id"])

        elif params_dict["action"] == "reject":
            call_scripts.reject_call(params_dict["call_id"], helper["_id"])

        elif params_dict["action"] == "comment":
            if 'comment' not in params_dict:
                return formatting.status('comment missing')

            call_scripts.comment_call(params_dict["call_id"], params_dict["comment"])
        else:
            return formatting.status('action invalid')



        # Step 5) Fetch new account state

        return fetching.get_all_helper_data(email=params_dict["email"])
