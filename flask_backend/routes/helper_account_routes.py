from flask_backend import app, helper_accounts_collection, status, api
from flask import redirect, request

from flask_backend.routes import support_functions
from flask_backend.nosql_scripts.helper_account_scripts import api_authentication, email_verification, phone_verification
from flask_backend.nosql_scripts.helper_account_scripts.support_functions import get_all_helper_data

from twilio.twiml.voice_response import VoiceResponse, Gather


import time



@app.route("/backend/login/helper", methods=["POST"])
def backend_helper_login():
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

    return login_result_dict




@app.route("/backend/logout/helper", methods=["POST"])
def backend_helper_logout():
    params_dict = support_functions.get_params_dict(request)

    if "email" not in params_dict or "api_key" not in params_dict:
        return status("missing parameter email/api_key")

    api_authentication.helper_logout(params_dict["email"], params_dict["api_key"])
    return status("ok")







from flask_backend.resources.rest_helper_account import RESTAccount
api.add_resource(RESTAccount, "/backend/database/account")






@app.route("/backend/email/verify/<verification_token>")
def backend_email_verify(verification_token):
    email_verification.verify_email(verification_token)
    return redirect("/calls")


@app.route("/backend/email/resend", methods=["POST"])
def backend_resend_email():
    params_dict = support_functions.get_params_dict(request)

    if "email" not in params_dict or "api_key" not in params_dict:
        return status("missing parameter email/api_key")

    else:
        login_dict = api_authentication.helper_login_api_key(params_dict["email"], params_dict["api_key"])
        if login_dict["status"] == "ok":

            helper_account = helper_accounts_collection.find_one({"email": params_dict["email"]})

            if not helper_account["email_verified"]:
                email_verification.trigger_email_verification(helper_account["_id"], helper_account["email"])
                return status("ok")
            else:
                return status("email already verified")
        else:
            return status("email/api_key invalid")




@app.route("/backend/phone/trigger", methods=["POST"])
def backend_trigger_phone_verification():
    params_dict = support_functions.get_params_dict(request)

    if "email" not in params_dict or "api_key" not in params_dict:
        return status("missing parameter email/api_key")

    if api_authentication.helper_login_api_key(params_dict["email"], params_dict["api_key"])["status"] != "ok":
        return {"status": "invalid request"}

    helper_account = helper_accounts_collection.find_one({"email": params_dict["email"]}, {"_id": 1})

    return phone_verification.trigger_phone_number_verification(helper_account["_id"])


@app.route("/backend/phone/verify", methods=['GET', 'POST'])
def hotline_phone_verification():

    # STEP 3) Are we allowed to call you back for feedback?

    resp = VoiceResponse()

    if 'Digits' in request.values:
        token = request.values['Digits']

        phone_number = support_functions.get_params_dict(request)["Caller"]
        verification_result = phone_verification.verify_phone_number(token=token, phone_number=phone_number)

        print(verification_result)

        if verification_result["status"] == "ok":
            resp.say("Your phone number has been confirmed successfully. Goodbye", voice="woman", language="en-gb")
            return str(resp)

    gather = Gather(num_digits=8, finish_on_key="#")
    gather.say("Please enter your confirmation code and confirm with the hash-key.", voice="woman", language="en-gb")
    resp.append(gather)

    resp.redirect('/backend/phone/verify')

    return str(resp)


@app.route("/backend/phone/confirm", methods=["POST"])
def backend_confirm_phone_verification():
    params_dict = support_functions.get_params_dict(request)

    if "email" not in params_dict or "api_key" not in params_dict:
        return status("missing parameter email/api_key")

    if api_authentication.helper_login_api_key(params_dict["email"], params_dict["api_key"])["status"] != "ok":
        return status("invalid request")

    helper_account = helper_accounts_collection.find_one({"email": params_dict["email"]})

    return phone_verification.confirm_phone_number_verification(helper_account)



