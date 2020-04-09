
from flask import request
from flask_backend import app
from twilio.twiml.voice_response import VoiceResponse, Gather

from flask_backend.nosql_scripts import call_scripts
from flask_backend.nosql_scripts.call_scripts import enqueue
from flask_backend.nosql_scripts.helper_account_scripts import forwarding
from flask_backend.routes.hotline_translation import hotline_translation

from flask_backend.routes import support_functions

language_translation = {
    'de': 'german',
    'en-gb': 'english'
}

def twilio_language_to_string(twilio_language):
    if twilio_language not in language_translation:
        return ''
    else:
        return language_translation[twilio_language]


@app.route('/hotline', methods=['GET', 'POST'])
def initial_endpoint():

    # STEP 1) Choose Language

    resp = VoiceResponse()

    if 'Digits' in request.values:
        choice = request.values['Digits']

        if choice == '1':
            resp.redirect(f'/hotline/de/question/1')
            return str(resp)
        elif choice == '2':
            resp.redirect(f'/hotline/en-gb/question/1')
            return str(resp)
        else:
            for language in ['de', 'en-gb']:
                resp.say(hotline_translation['unknown_option'][language], voice='woman', language=language)

    gather = Gather(num_digits=1)
    for language in ['de', 'en-gb']:
        gather.say(hotline_translation['choose_language'][language], voice='woman', language=language)
    resp.append(gather)

    resp.redirect(f'/hotline')

    return str(resp)


@app.route('/hotline/<language>/question/1', methods=['GET', 'POST'])
def hotline_question_1(language):

    # STEP 2) Local Help or Independet of Location?
    #         if local: redirect to zip_code captcha
    #         else: generate caller and call record -> redirect to feedback captcha

    resp = VoiceResponse()

    if 'Digits' in request.values:
        choice = request.values['Digits']

        if choice == '1':
            resp.redirect(f'/hotline/{language}/question/2')
            return str(resp)
        elif choice == '2':
            caller_id = call_scripts.add_caller(support_functions.get_params_dict(request)['Caller'])['caller_id']
            call_id = call_scripts.add_call(caller_id, twilio_language_to_string(language), call_type='global')['call_id']
            resp.redirect(f'/hotline/{language}/question/3/{call_id}')
            return str(resp)
        else:
            resp.say(hotline_translation['unknown_option'][language], voice='woman', language=language)

    gather = Gather(num_digits=1)
    gather.say(hotline_translation['question_1_text_1'][language], voice='woman', language=language)
    resp.append(gather)

    resp.redirect(f'/hotline/{language}/question/1')

    return str(resp)


@app.route('/hotline/<language>/question/2', methods=['GET', 'POST'])
def hotline_question_2(language):

    # STEP 2.5) Enter zip code -> generate caller and call record

    resp = VoiceResponse()
    gather = Gather(num_digits=6, finish_on_key='#')

    if 'Digits' in request.values:

        zip_code = request.values['Digits']
        finished_on_key = request.values['FinishedOnKey']

        if len(zip_code) == 5 and finished_on_key == '#':

            caller_id = call_scripts.add_caller(support_functions.get_params_dict(request)['Caller'])['caller_id']
            call_id = call_scripts.add_call(caller_id, twilio_language_to_string(language), call_type='local', zip_code=zip_code)['call_id']
            resp.redirect(f'/hotline/{language}/question/3/{call_id}')
            return str(resp)

    gather.say(hotline_translation['question_2_text_1'][language], voice='woman', language=language)
    resp.append(gather)

    resp.redirect(f'/hotline/{language}/question/2')

    return str(resp)


@app.route('/hotline/<language>/question/3/<call_id>', methods=['GET', 'POST'])
def hotline_question_3(language, call_id):

    # STEP 3) Are we allowed to call you back for feedback?

    resp = VoiceResponse()
    gather = Gather(num_digits=1)

    if 'Digits' in request.values:
        choice = request.values['Digits']

        if choice in ['1', '2']:
            call_scripts.set_feeback(call_id, (choice == '1'))
            resp.redirect(f'/hotline/{language}/question/4/{call_id}')
            return str(resp)
        else:
            resp.say(hotline_translation['unknown_option'][language], voice='woman', language=language)
            gather.say(hotline_translation['question_3_text_2'][language], voice='woman', language=language)
    else:
        gather.say(hotline_translation['question_3_text_1'][language], voice='woman', language=language)

    gather.say(hotline_translation['question_3_text_3'][language], voice='woman', language=language)
    resp.append(gather)

    resp.redirect(f'/hotline/{language}/question/3/{call_id}')

    return str(resp)


@app.route('/hotline/<language>/question/4/<call_id>', methods=['GET', 'POST'])
def hotline_question_4(language, call_id):

    # STEP 4) Confirm or Cancel the Call

    resp = VoiceResponse()
    gather = Gather(num_digits=1)

    if 'Digits' in request.values:
        choice = request.values['Digits']

        if choice == '1':
            # TODO: Async Task - maybe Celery?
            call_scripts.set_confirmed(call_id, True)
            resp.say(hotline_translation['question_4_answer_confirm'][language], voice='woman', language=language)
            resp.redirect(f'/hotline/{language}/forward/{call_id}')
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

    resp.redirect(f'/hotline/{language}/question/4/{call_id}')

    return str(resp)


@app.route('/hotline/<language>/forward/<call_id>', methods=['GET', 'POST'])
def hotline_forward(language, call_id):

    forward_helper_query_result = forwarding.find_forward_helper(call_id)

    resp = VoiceResponse()

    if forward_helper_query_result["status"] == "ok":
        resp.say(hotline_translation['forward_successful'][language], voice='woman', language=language)

        phone_number = forward_helper_query_result["phone_number"]
        helper_id = forward_helper_query_result['helper_id']
        resp.dial(phone_number,
                  action=f"/hotline/{language}/after-forward/{call_id}/{helper_id}",
                  timeout=15)

    else:
        resp.say(hotline_translation['forward_not_successful'][language], voice='woman', language=language)
        enqueue.enqueue(call_id)

    return str(resp)


@app.route('/hotline/<language>/after-forward/<call_id>/<helper_id>', methods=['GET', 'POST'])
def hotline_after_forward(language, call_id, helper_id):

    forward_call_result = support_functions.get_params_dict(request)
    dial_call_status = forward_call_result["DialCallStatus"]

    resp = VoiceResponse()

    if dial_call_status == "completed":
        resp.say(hotline_translation['after_forward_successful'][language], voice='woman', language=language)
    else:
        forwarding.flag_helper(call_id, helper_id, dial_call_status)
        enqueue.enqueue(call_id)
        resp.say(hotline_translation['after_forward_not_successful'][language], voice='woman', language=language)

    return str(resp)




@app.route('/hotline/error', methods=['GET', 'POST'])
def hotline_error():

    # Error response in case the server does not produce a valid response at some point

    resp = VoiceResponse()

    for language in ['de', 'en-gb']:
        resp.say(hotline_translation['error_message'][language], voice='woman', language=language)

    return str(resp)
