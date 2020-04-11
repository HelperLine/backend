
from flask_backend import app, api, FRONTEND_URL
from flask_backend.database_scripts.helper_scripts import api_authentication, email_verification, phone_verification
from flask_backend.support_functions import routing, tokening, formatting

from twilio.twiml.voice_response import VoiceResponse, Gather
from flask import redirect, request
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
            login_result_dict = formatting.status('email/password/api_key missing')

        return login_result_dict

    else:
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
        return formatting.status("api_version invalid")


@app.route('/backend/<api_version>/email/verify/<verification_token>')
def route_helper_email_verify(api_version, verification_token):

    if api_version == "v1":
        email_verification.verify_email(verification_token)
        return redirect(FRONTEND_URL + 'calls')

    else:
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
        return formatting.status("api_version invalid")


@app.route('/backend/<api_version>/phone/verify', methods=['GET', 'POST'])
def route_helper_phone_verify(api_version):

    if api_version == "v1":
        resp = VoiceResponse()

        if 'Digits' in request.values:
            token = request.values['Digits']

            phone_number = routing.get_params_dict(request)['Caller']
            verification_result = phone_verification.verify_phone_number(token=token, phone_number=phone_number)

            if verification_result['status'] == 'ok':
                resp.say('Your phone number has been confirmed successfully. Goodbye', voice='woman', language='en-gb')
                return str(resp)

        gather = Gather(num_digits=8, finish_on_key='#')
        gather.say('Please enter your confirmation code and confirm with the hash-key.', voice='woman', language='en-gb')
        resp.append(gather)

        resp.redirect('/backend/v1/phone/verify')

        return str(resp)

    else:
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
        return formatting.status("api_version invalid")
