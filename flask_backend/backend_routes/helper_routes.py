
from flask_backend import app, api
from flask_backend.database_scripts.helper_scripts import api_authentication, email_verification, phone_verification
from flask_backend.support_functions import routing, tokening, formatting

from flask import request
import time


from flask_backend.restful_resources.rest_helper import RESTHelper
api.add_resource(RESTHelper, '/backend/v1/database/helper')


@app.route('/backend/<api_version>/login/helper', methods=['POST'])
def route_helper_account_login(api_version):

    if api_version == "v1":
        params_dict = routing.get_params_dict(request)

        # Artificial delay to further prevent brute forcing
        time.sleep(0.05)

        email = params_dict['email']
        password = params_dict['password']
        api_key = params_dict['api_key']

        # Initial login
        if email is not None and password is not None:
            login_result_dict = api_authentication.helper_login_password(email, password)

        # Automatic re-login from webapp
        elif email is not None and api_key is not None:
            login_result_dict = api_authentication.helper_login_api_key(email, api_key)

        else:
            # Programming Error
            login_result_dict = formatting.status('email/password/api_key missing')

        return login_result_dict

    else:
        # Programming Error
        return formatting.status("api_version invalid")


@app.route('/backend/<api_version>/logout/helper', methods=['POST'])
def route_helper_account_logout(api_version):

    if api_version == "v1":
        params_dict = routing.get_params_dict(request)

        authentication_result = tokening.check_helper_api_key(params_dict)
        if authentication_result["status"] != "ok":
            return authentication_result

        return api_authentication.helper_logout(params_dict['email'], params_dict['api_key'])

    else:
        # Programming Error
        return formatting.status("api_version invalid")


@app.route('/backend/<api_version>/email/resend', methods=['POST'])
def route_helper_email_resend(api_version):

    if api_version == "v1":
        params_dict = routing.get_params_dict(request)

        authentication_result = tokening.check_helper_api_key(params_dict)
        if authentication_result["status"] != "ok":
            return authentication_result

        return email_verification.trigger_email_verification(params_dict['email'])

    else:
        # Programming Error
        return formatting.status("api_version invalid")


@app.route('/backend/<api_version>/phone/trigger', methods=['POST'])
def route_helper_phone_trigger(api_version):

    if api_version == "v1":
        params_dict = routing.get_params_dict(request)

        authentication_result = tokening.check_helper_api_key(params_dict)
        if authentication_result["status"] != "ok":
            return authentication_result

        return phone_verification.trigger_phone_verification(params_dict['email'])

    else:
        # Programming Error
        return formatting.status("api_version invalid")


@app.route('/backend/<api_version>/phone/confirm', methods=['POST'])
def route_helper_phone_confirm(api_version):

    if api_version == "v1":
        params_dict = routing.get_params_dict(request)

        authentication_result = tokening.check_helper_api_key(params_dict)
        if authentication_result["status"] != "ok":
            return authentication_result

        return phone_verification.confirm_phone_verification(params_dict['email'])

    else:
        # Programming Error
        return formatting.status("api_version invalid")
