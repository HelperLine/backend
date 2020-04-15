
from flask_backend import app
from flask_backend.database_scripts.helper_scripts.api_authentication import helper_login_password, helper_login_api_key, helper_logout
from flask_backend.database_scripts.admin_scripts.api_authentication import admin_login_password, admin_login_api_key, admin_logout
from flask_backend.support_functions import routing, tokening, formatting

from flask import request
import time


@app.route('/<api_version>/authentication/login/<account_type>', methods=['POST'])
def route_authentication_login(api_version, account_type):

    if api_version == "v1":

        params_dict = routing.get_params_dict(request)

        # Artificial delay to further prevent brute forcing
        time.sleep(0.05)

        email = params_dict['email']
        password = params_dict['password']
        api_key = params_dict['api_key']

        if account_type == "helper":

            # Initial login
            if email is not None and password is not None:
                return helper_login_password(email, password)

            # Automatic re-login from webapp
            elif email is not None and api_key is not None:
                return helper_login_api_key(email, api_key)

        elif account_type == "admin":

            # initial login
            if email is not None and password is not None:
                return admin_login_password(email, password)

            # automatic re-login from webapp
            elif email is not None and api_key is not None:
                return admin_login_api_key(email, api_key)

        else:
            return formatting.status("account_type invalid")

        return formatting.status('email/password/api_key missing')

    else:
        # Programming Error
        return formatting.status("api_version invalid")


@app.route('/<api_version>/authentication/logout/<account_type>', methods=['POST'])
def route_authentication_logout(api_version, account_type):

    if api_version == "v1":

        params_dict = routing.get_params_dict(request)

        if account_type == "helper":
            authentication_result = tokening.check_helper_api_key(params_dict)
            if authentication_result["status"] != "ok":
                return authentication_result

            return helper_logout(params_dict['email'], params_dict['api_key'])

        elif account_type == "admin":
            authentication_result = tokening.check_admin_api_key(params_dict)
            if tokening.check_admin_api_key(params_dict)["status"] != "ok":
                return authentication_result

            return admin_logout(params_dict['email'], params_dict['api_key'])

        else:
            return formatting.status("account_type invalid")
    else:
        # Programming Error
        return formatting.status("api_version invalid")