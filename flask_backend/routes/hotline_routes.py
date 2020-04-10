
from flask_backend import app
from flask_backend.database_scripts import call_scripts
from flask_backend.database_scripts.call_scripts import enqueue
from flask_backend.database_scripts.helper_account_scripts import forwarding
from flask_backend.support_functions import routing

from flask_backend.routes.hotline_translation import hotline_translation

from twilio.twiml.voice_response import VoiceResponse, Gather
from flask import request


language_translation = {
    'de': 'german',
    'en-gb': 'english'
}

def twilio_language_to_string(twilio_language):
    if twilio_language not in language_translation:
        return ''
    else:
        return language_translation[twilio_language]


@app.route('/hotline/<api_version>', methods=['GET', 'POST'])
def route_initial_endpoint(api_version):
    
    resp = VoiceResponse()
    
    if api_version == "v1":
        # STEP 1) Choose Language
    
        if 'Digits' in request.values:
            choice = request.values['Digits']
    
            if choice == '1':
                resp.redirect(f'/hotline/{api_version}/de/question/1')
                return str(resp)
            elif choice == '2':
                resp.redirect(f'/hotline/{api_version}/en-gb/question/1')
                return str(resp)
            else:
                for language in ['de', 'en-gb']:
                    resp.say(hotline_translation['unknown_option'][language], voice='woman', language=language)
    
        gather = Gather(num_digits=1)
        for language in ['de', 'en-gb']:
            gather.say(hotline_translation['choose_language'][language], voice='woman', language=language)
        resp.append(gather)
    
        resp.redirect(f'/hotline/{api_version}')
    
    else:
        resp.redirect('/hotline/error/api_version')

    return str(resp)


@app.route('/hotline/<api_version>/<language>/question/1', methods=['GET', 'POST'])
def route_hotline_question_1(api_version, language):
    
    resp = VoiceResponse()

    if api_version == "v1":
        # STEP 2) Local Help or Independet of Location?
        #         if local: redirect to zip_code captcha
        #         else: generate caller and call record -> redirect to feedback captcha
    
        if 'Digits' in request.values:
            choice = request.values['Digits']
    
            if choice == '1':
                resp.redirect(f'/hotline/{api_version}/{language}/question/2')
                return str(resp)
            elif choice == '2':
                caller_id = call_scripts.add_caller(routing.get_params_dict(request)['Caller'])['caller_id']
                call_id = call_scripts.add_call(caller_id, twilio_language_to_string(language), call_type='global')['call_id']
                resp.redirect(f'/hotline/{api_version}/{language}/question/3/{call_id}')
                return str(resp)
            else:
                resp.say(hotline_translation['unknown_option'][language], voice='woman', language=language)
    
        gather = Gather(num_digits=1)
        gather.say(hotline_translation['question_1_text_1'][language], voice='woman', language=language)
        resp.append(gather)
    
        resp.redirect(f'/hotline/{api_version}/{language}/question/1')

    else:
        resp.redirect('/hotline/error/api_version')

    return str(resp)


@app.route('/hotline/<api_version>/<language>/question/2', methods=['GET', 'POST'])
def route_hotline_question_2(api_version, language):
    
    resp = VoiceResponse()

    if api_version == "v1":
        # STEP 2.5) Enter zip code -> generate caller and call record
    
        gather = Gather(num_digits=6, finish_on_key='#')
    
        if 'Digits' in request.values:
    
            zip_code = request.values['Digits']
            finished_on_key = request.values['FinishedOnKey']
    
            if len(zip_code) == 5 and finished_on_key == '#':
    
                caller_id = call_scripts.add_caller(routing.get_params_dict(request)['Caller'])['caller_id']
                call_id = call_scripts.add_call(caller_id, twilio_language_to_string(language), call_type='local', zip_code=zip_code)['call_id']
                resp.redirect(f'/hotline/{api_version}/{language}/question/3/{call_id}')
                return str(resp)
    
        gather.say(hotline_translation['question_2_text_1'][language], voice='woman', language=language)
        resp.append(gather)
    
        resp.redirect(f'/hotline/{api_version}/{language}/question/2')
    
    else:
        resp.redirect('/hotline/error/api_version')

    return str(resp)


@app.route('/hotline/<api_version>/<language>/question/3/<call_id>', methods=['GET', 'POST'])
def route_hotline_question_3(api_version, language, call_id):
    
    resp = VoiceResponse()

    if api_version == "v1":
        # STEP 3) Are we allowed to call you back for feedback?

        gather = Gather(num_digits=1)
    
        if 'Digits' in request.values:
            choice = request.values['Digits']
    
            if choice in ['1', '2']:
                call_scripts.set_feeback(call_id, (choice == '1'))
                resp.redirect(f'/hotline/{api_version}/{language}/question/4/{call_id}')
                return str(resp)
            else:
                resp.say(hotline_translation['unknown_option'][language], voice='woman', language=language)
                gather.say(hotline_translation['question_3_text_2'][language], voice='woman', language=language)
        else:
            gather.say(hotline_translation['question_3_text_1'][language], voice='woman', language=language)
    
        gather.say(hotline_translation['question_3_text_3'][language], voice='woman', language=language)
        resp.append(gather)
    
        resp.redirect(f'/hotline/{api_version}/{language}/question/3/{call_id}')
    
    else:
        resp.redirect('/hotline/error/api_version')

    return str(resp)


@app.route('/hotline/<api_version>/<language>/question/4/<call_id>', methods=['GET', 'POST'])
def route_hotline_question_4(api_version, language, call_id):
    
    resp = VoiceResponse()

    if api_version == "v1":
        # STEP 4) Confirm or Cancel the Call

        gather = Gather(num_digits=1)
    
        if 'Digits' in request.values:
            choice = request.values['Digits']
    
            if choice == '1':
                # TODO: Async Task - maybe Celery?
                call_scripts.set_confirmed(call_id, True)
                resp.say(hotline_translation['question_4_answer_confirm'][language], voice='woman', language=language)
                resp.redirect(f'/hotline/{api_version}/{language}/forward/{call_id}')
                return str(resp)
            elif choice == '2':
                # TODO: Async Task - maybe Celery?
                call_scripts.set_confirmed(call_id, False)
                resp.say(hotline_translation['question_4_answer_cancel'][language], voice='woman', language=language)
                return str(resp)
            else:
                resp.say(hotline_translation['unknown_option'][language], voice='woman', language=language)
    
        gather.say(hotline_translation['question_4_text_1'][language], voice='woman', language=language)
        resp.append(gather)
    
        resp.redirect(f'/hotline/{api_version}/{language}/question/4/{call_id}')
    
    else:
        resp.redirect('/hotline/error/api_version')

    return str(resp)


@app.route('/hotline/<api_version>/<language>/forward/<call_id>', methods=['GET', 'POST'])
def route_hotline_forward(api_version, language, call_id):
    
    resp = VoiceResponse()

    if api_version == "v1":
        forward_helper_query_result = forwarding.find_forward_helper(call_id)

        if forward_helper_query_result["status"] == "ok":
            resp.say(hotline_translation['forward_successful'][language], voice='woman', language=language)
    
            phone_number = forward_helper_query_result["phone_number"]
            helper_id = forward_helper_query_result['helper_id']
            resp.dial(phone_number,
                      action=f"/hotline/{api_version}/{language}/after-forward/{call_id}/{helper_id}",
                      timeout=15)
    
        else:
            resp.say(hotline_translation['forward_not_successful'][language], voice='woman', language=language)
            enqueue.enqueue(call_id)
    
    else:
        resp.redirect('/hotline/error/api_version')

    return str(resp)


@app.route('/hotline/<api_version>/<language>/after-forward/<call_id>/<helper_id>', methods=['GET', 'POST'])
def route_hotline_after_forward(api_version, language, call_id, helper_id):
    
    resp = VoiceResponse()

    if api_version == "v1":
        forward_call_result = routing.get_params_dict(request)
        dial_call_status = forward_call_result["DialCallStatus"]

        if dial_call_status == "completed":
            resp.say(hotline_translation['after_forward_successful'][language], voice='woman', language=language)
        else:
            forwarding.flag_helper(call_id, helper_id, dial_call_status)
            enqueue.enqueue(call_id)
            resp.say(hotline_translation['after_forward_not_successful'][language], voice='woman', language=language)

    else:
        resp.redirect('/hotline/error/api_version')

    return str(resp)




@app.route('/hotline/error/general', methods=['GET', 'POST'])
def route_hotline_error_general():

    # Error response in case the server does not produce a valid response at some point

    resp = VoiceResponse()

    for language in ['de', 'en-gb']:
        resp.say(hotline_translation['error_message_general'][language], voice='woman', language=language)

    return str(resp)


@app.route('/hotline/error/api_version', methods=['GET', 'POST'])
def route_hotline_error_api_version():

    # Error response in case an invalid api_version is requested

    resp = VoiceResponse()

    for language in ['de', 'en-gb']:
        resp.say(hotline_translation['error_message_api_version'][language], voice='woman', language=language)

    return str(resp)
