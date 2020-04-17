
from flask_backend import app
from flask_backend.database_scripts.verification_scripts import phone_verification
from flask_backend.backend_routes.hotline_routes.hotline_translation import hotline_translation
from flask_backend.support_functions import routing

from twilio.twiml.voice_response import VoiceResponse, Gather
from flask import request


@app.route('/<api_version>/verification/phone/hotline', methods=['GET', 'POST'])
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


@app.route('/<api_version>/verification/phone/hotline/<language>', methods=['GET', 'POST'])
def route_verification_phone_code(api_version, language):

    resp = VoiceResponse()

    if api_version == "v1":
        if language in ["de", "en-gb"]:
            if 'Digits' in request.values:
                token = request.values['Digits']
                finished_on_key = request.values['FinishedOnKey']

                if len(token) == 5 and finished_on_key == '#':
                    phone_number = routing.get_params_dict(request)['Caller']
                    verification_result = phone_verification.verify(token, phone_number)

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
            resp.redirect('/v1/hotline/error/language')
    else:
        # Programming Error
        resp.redirect('/v1/hotline/error/api_version')

    return str(resp)
