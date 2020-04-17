
from flask_backend import app
from flask_backend.database_scripts.authentication_scripts.helper_authentication import helper_login_password, helper_login_api_key
from flask_backend.database_scripts.authentication_scripts.admin_authentication import admin_login_password, admin_login_api_key
from flask_backend.support_functions import routing, formatting

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
                login_result = helper_login_password(email, password)
                return formatting.postprocess_response(login_result)

            # Automatic re-login from webapp
            elif email is not None and api_key is not None:
                login_result = helper_login_api_key(email, api_key)
                return formatting.postprocess_response(login_result)

        elif account_type == "admin":

            # initial login
            if email is not None and password is not None:
                login_result = admin_login_password(email, password)
                return formatting.postprocess_response(login_result)

            # automatic re-login from webapp
            elif email is not None and api_key is not None:
                login_result = admin_login_api_key(email, api_key)
                return formatting.postprocess_response(login_result)

        else:
            return formatting.status("account_type invalid"), 400

        return formatting.status('email/password/api_key missing'), 400

    else:
        # Programming Error
        return formatting.status("api_version invalid"), 400
