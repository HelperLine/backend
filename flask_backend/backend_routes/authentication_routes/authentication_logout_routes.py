
from flask_backend import app
from flask_backend.database_scripts.authentication_scripts.helper_authentication import helper_logout
from flask_backend.database_scripts.authentication_scripts.admin_authentication import admin_logout
from flask_backend.support_functions import routing, tokening, formatting

from flask import request


@app.route('/<api_version>/authentication/logout/<account_type>', methods=['POST'])
def route_authentication_logout(api_version, account_type):

    if api_version == "v1":

        params_dict = routing.get_params_dict(request)

        if account_type == "helper":
            authentication_result = tokening.check_helper_api_key(params_dict)
            if authentication_result["status"] != "ok":
                return formatting.postprocess_response(authentication_result)

            # Route will always return {"status": "ok"}
            return helper_logout(params_dict['email'], params_dict['api_key']), 200

        elif account_type == "admin":
            authentication_result = tokening.check_admin_api_key(params_dict)
            if tokening.check_admin_api_key(params_dict)["status"] != "ok":
                return formatting.postprocess_response(authentication_result)

            # Route will always return {"status": "ok"}
            return admin_logout(params_dict['email'], params_dict['api_key']), 200

        else:
            return formatting.status("account_type invalid"), 400
    else:
        # Programming Error
        return formatting.status("api_version invalid"), 400
