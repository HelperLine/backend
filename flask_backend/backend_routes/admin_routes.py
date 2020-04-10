
from flask_backend.database_scripts.admin_scripts import api_authentication
from flask_backend.support_functions import routing, tokening

from flask_backend import app, status
from flask import request
import time


@app.route('/backend/<api_version>/login/admin', methods=['POST'])
def route_admin_account_login(api_version):

    if api_version == "v1":
        params_dict = routing.get_params_dict(request)

        # Artificial delay to further prevent brute forcing
        time.sleep(0.05)

        email = params_dict['email']
        password = params_dict['password']
        api_key = params_dict['api_key']

        # initial login
        if email is not None and password is not None:
            return api_authentication.admin_login_password(email, password)

        # automatic re-login from webapp
        elif email is not None and api_key is not None:
            return api_authentication.admin_login_api_key(email, api_key)

        # invalid request
        else:
            return status('email/password/api_key missing')

    else:
        return status("api_version invalid")




@app.route('/backend/<api_version>/logout/admin', methods=['POST'])
def route_admin_account_logout(api_version):

    if api_version == "v1":
        params_dict = routing.get_params_dict(request)

        authentication_result = tokening.check_admin_api_key(params_dict)
        if authentication_result["status"] != "ok":
            return authentication_result

        return api_authentication.admin_logout(params_dict['email'], params_dict['api_key'])

    else:
        return status("api_version invalid")
