
from flask_backend import app, FRONTEND_URL
from flask_backend.database_scripts.helper_scripts import email_verification, phone_verification
from flask_backend.support_functions import routing, formatting
from flask_backend.backend_routes.hotline_translation import hotline_translation

from twilio.twiml.voice_response import VoiceResponse, Gather
from flask import redirect, request


@app.route('/verification/<api_version>/email/<verification_token>')
def route_verification_email(api_version, verification_token):

    if api_version == "v1":
        email_verification.verify_email(verification_token)
        return redirect(FRONTEND_URL + 'calls')

    else:
        # Programming Error
        return formatting.status("api_version invalid")


@app.route('/verification/<api_version>/phone', methods=['GET', 'POST'])
def route_verification_phone(api_version):
    resp = VoiceResponse()

    if api_version == "v1":
        # STEP 1) Choose Language

        if 'Digits' in request.values:
            choice = request.values['Digits']

            if choice == '1':
                resp.redirect(f'/verification/{api_version}/de/phone/code')
                return str(resp)
            elif choice == '2':
                resp.redirect(f'/verification/{api_version}/en-gb/phone/code')
                return str(resp)
            else:
                for language in ['de', 'en-gb']:
                    resp.say(hotline_translation['unknown_option'][language], voice='woman', language=language)

        gather = Gather(num_digits=1)
        for language in ['de', 'en-gb']:
            gather.say(hotline_translation['choose_language'][language], voice='woman', language=language)
        resp.append(gather)

        resp.redirect(f'/verification/{api_version}/phone')

    else:
        resp.redirect('/hotline/error/api_version')

    return str(resp)


@app.route('/verification/<api_version>/<language>/phone/code', methods=['GET', 'POST'])
def route_verification_phone_code(api_version, language):

    resp = VoiceResponse()

    if api_version == "v1":
        if 'Digits' in request.values:
            token = request.values['Digits']
            finished_on_key = request.values['FinishedOnKey']

            if len(token) == 5 and finished_on_key == '#':
                phone_number = routing.get_params_dict(request)['Caller']
                verification_result = phone_verification.verify_phone_number(token=token, phone_number=phone_number)

                if verification_result['status'] == 'ok':
                    resp.say(hotline_translation['verification_success'][language], voice='woman', language=language)
                    return str(resp)
                else:
                    resp.say(hotline_translation['verification_fail'][language], voice='woman', language=language)


        gather = Gather(num_digits=6, finish_on_key='#')
        gather.say(hotline_translation['verification_enter_code'][language], voice='woman', language=language)
        resp.append(gather)

        resp.redirect(f'/backend/{api_version}/{language}/phone/code')

    else:
        # Programming Error
        resp.redirect('/hotline/error/api_version')

    return str(resp)
