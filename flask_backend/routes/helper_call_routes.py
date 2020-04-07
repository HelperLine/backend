
from flask_backend import app, status, helper_accounts_collection
from flask_backend.routes import support_functions as support_functions_rest
from flask_backend.nosql_scripts.helper_account_scripts import api_authentication
from flask_backend.nosql_scripts.helper_account_scripts.support_functions import get_all_helper_data

from flask_backend.nosql_scripts.call_scripts import dequeue, fulfill_call, reject_call

from flask import request



@app.route("/backend/calls/accept", methods=["POST"])
def accept_call_route():
    params_dict = support_functions_rest.get_params_dict(request, print_out=True)

    if api_authentication.helper_login_api_key(params_dict["email"], params_dict["api_key"])["status"] != "ok":
        return status("invalid request")

    helper = helper_accounts_collection.find_one({"email": params_dict["email"]})

    if helper is None:
        return status("invalid request")

    if "filter_type_local" not in params_dict or "filter_type_global" not in params_dict or \
            "filter_language_german" not in params_dict or "filter_language_english" not in params_dict:
        return status("invalid request")

    print(f"helper: {helper}")

    dequeue_result = dequeue.dequeue(
        helper["_id"],
        zip_code=helper["zip_code"],
        only_local_calls=params_dict["filter_type_local"],
        only_global_calls=params_dict["filter_type_global"],
        accept_german=params_dict["filter_language_german"],
        accept_english=params_dict["filter_language_english"]
    )

    if dequeue_result["status"] != "ok":
        return dequeue_result
    else:
        return get_all_helper_data(helper_id=helper["_id"])


@app.route("/backend/calls/fulfill", methods=["POST"])
def fulfill_call_route():
    return status("ok")


@app.route("/backend/calls/reject", methods=["POST"])
def reject_call_route():
    return status("ok")







