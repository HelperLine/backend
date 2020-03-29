from flask_backend import app, helper_accounts_collection, status, api
from flask import redirect, request

from flask_backend.routes import support_functions
from flask_backend.nosql_scripts.helper_account_scripts import api_authentication, email_verification

import time



@app.route("/backend/login/helper", methods=["POST"])
def backend_login():
    params_dict = support_functions.get_params_dict(request)

    # Artificial delay to further prevent brute forcing
    time.sleep(0.05)

    print(params_dict)

    email = params_dict["email"]
    password = params_dict["password"]
    api_key = params_dict["api_key"]

    # Initial login
    if email is not None and password is not None:
        login_result_dict = api_authentication.helper_login_password(email, password)

    # Automatic re-login from webapp
    elif email is not None and api_key is not None:
        # TODO: Generate new API Key for every login request in production!
        login_result_dict = api_authentication.helper_login_api_key(email, api_key)

    else:
        login_result_dict = status("missing parameter email/password/api_key")

    if login_result_dict["status"] == "ok":
        helper_account = helper_accounts_collection.find_one({"email": email})

        account_dict = {
            "email_verified": helper_account["email_verified"],
            "zip_code": helper_account["zip_code"],
            "country": helper_account["country"],
        }

        # TODO: Add real calls dict
        calls_dict = {
            "accepted": [],
            "fulfilled": []
        }
        login_result_dict.update({"account": account_dict, "calls": calls_dict})

    return login_result_dict, 200




@app.route("/backend/logout/helper", methods=["POST"])
def backend_logout():
    params_dict = support_functions.get_params_dict(request)

    if "email" not in params_dict or "api_key" not in params_dict:
        return {"Status": "missing parameter email/api_key"}, 200

    api_authentication.logout_account(params_dict["email"], params_dict["api_key"])
    return {"status": "ok"}, 200







@app.route("/backend/email/verify/<verification_token>")
def backend_email_verify(verification_token):
    email_verification.verify_email(verification_token)
    return redirect("/calls")


@app.route("/backend/email/resend", methods=["POST"])
def backend_resend_email():
    params_dict = support_functions.get_params_dict(request)

    if "email" not in params_dict or "api_key" not in params_dict:
        return {"status": "missing parameter email/api_key"}, 200

    else:
        login_dict = api_authentication.helper_login_api_key(params_dict["email"], params_dict["api_key"])
        if login_dict["status"] == "ok":

            helper_account = helper_accounts_collection.find_one({"email": params_dict["email"]})

            if not helper_account["email_verified"]:
                email_verification.trigger_email_verification(helper_account["_id"], helper_account["email"])
                return {"status": "ok"}, 200
            else:
                return {"status": "email already verified"}, 200
        else:
            return {"status": "email/api_key invalid"}, 200



from flask_backend.resources.rest_helper_account import RESTAccount
api.add_resource(RESTAccount, "/backend/database/account")
