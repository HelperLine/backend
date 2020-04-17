
from flask_backend import app
from flask_backend.database_scripts.verification_scripts import phone_verification
from flask_backend.support_functions import routing, tokening, formatting

from flask import request


@app.route('/<api_version>/phone/form/trigger', methods=['POST'])
def route_helper_phone_trigger(api_version):

    if api_version == "v1":
        params_dict = routing.get_params_dict(request)

        authentication_result = tokening.check_helper_api_key(params_dict)
        if authentication_result["status"] != "ok":
            return authentication_result

        return phone_verification.trigger(params_dict['email'])

    else:
        # Programming Error
        return formatting.status("api_version invalid")


@app.route('/<api_version>/phone/form/fetch', methods=['POST'])
def route_helper_phone_fetch(api_version):

    if api_version == "v1":
        params_dict = routing.get_params_dict(request)

        authentication_result = tokening.check_helper_api_key(params_dict)
        if authentication_result["status"] != "ok":
            return authentication_result

        return phone_verification.fetch(params_dict['email'])

    else:
        # Programming Error
        return formatting.status("api_version invalid")


@app.route('/<api_version>/phone/form/confirm', methods=['POST'])
def route_helper_phone_confirm(api_version):

    if api_version == "v1":
        params_dict = routing.get_params_dict(request)

        authentication_result = tokening.check_helper_api_key(params_dict)
        if authentication_result["status"] != "ok":
            return authentication_result

        return phone_verification.confirm(params_dict['email'])

    else:
        # Programming Error
        return formatting.status("api_version invalid")
