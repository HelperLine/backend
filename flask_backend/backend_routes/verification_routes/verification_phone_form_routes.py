
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
            return formatting.postprocess_response(authentication_result)

        result_dict = phone_verification.trigger(params_dict['email'])
        return formatting.postprocess_response(result_dict)

    else:
        # Programming Error
        return formatting.status("api_version invalid"), 400


@app.route('/<api_version>/phone/form/fetch', methods=['GET'])
def route_helper_phone_fetch(api_version):

    if api_version == "v1":
        params_dict = routing.get_params_dict(request)

        authentication_result = tokening.check_helper_api_key(params_dict, new_api_key=True)
        if authentication_result["status"] != "ok":
            return formatting.postprocess_response(authentication_result)

        result_dict = phone_verification.fetch(params_dict['email'])
        return formatting.postprocess_response(result_dict, new_api_key=authentication_result["api_key"])

    else:
        # Programming Error
        return formatting.status("api_version invalid"), 400


@app.route('/<api_version>/phone/form/confirm', methods=['POST'])
def route_helper_phone_confirm(api_version):

    if api_version == "v1":
        params_dict = routing.get_params_dict(request)

        authentication_result = tokening.check_helper_api_key(params_dict)
        if authentication_result["status"] != "ok":
            return formatting.postprocess_response(authentication_result)

        result_dict = phone_verification.confirm(params_dict['email'])
        return formatting.postprocess_response(result_dict)

    else:
        # Programming Error
        return formatting.status("api_version invalid"), 400
