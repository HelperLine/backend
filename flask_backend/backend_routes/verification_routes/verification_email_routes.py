from flask_backend import app, FRONTEND_URL
from flask_backend.database_scripts.verification_scripts import email_verification
from flask_backend.support_functions import routing, tokening, formatting

from flask import redirect, request


@app.route('/<api_version>/verification/email/resend', methods=['POST'])
def route_helper_email_resend(api_version):

    if api_version == "v1":
        params_dict = routing.get_params_dict(request)

        authentication_result = tokening.check_helper_api_key(params_dict)
        if authentication_result["status"] != "ok":
            return formatting.postprocess_response(authentication_result)

        result_dict = email_verification.trigger(params_dict['email'])
        return formatting.postprocess_response(result_dict)

    else:
        # Programming Error
        return formatting.status("api_version invalid"), 400


@app.route('/<api_version>/verification/email/verify/<verification_token>', methods=['GET'])
def route_verification_email(api_version, verification_token):

    if api_version == "v1":
        email_verification.verify(verification_token)
        return redirect(FRONTEND_URL + 'calls'), 302

    else:
        # Programming Error
        return formatting.status("api_version invalid"), 400
