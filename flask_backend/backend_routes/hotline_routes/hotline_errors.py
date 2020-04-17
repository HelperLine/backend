
from flask_backend import app
from flask_backend.backend_routes.hotline_routes.hotline_translation import hotline_translation

from twilio.twiml.voice_response import VoiceResponse


@app.route('/<api_version>/hotline/error/general', methods=['GET', 'POST'])
def route_hotline_error_general(api_version):
    # Error response in case the server does not produce a valid response at some point

    resp = VoiceResponse()

    if api_version == "v1":
        for language in ['de', 'en-gb']:
            resp.say(hotline_translation['error_message_general'][language], voice='woman', language=language)
    else:
        resp.redirect('/v1/hotline/error/api_version')

    return str(resp)


@app.route('/<api_version>/hotline/error/api_version', methods=['GET', 'POST'])
def route_hotline_error_api_version(api_version):
    # Error response in case an invalid api_version is requested

    resp = VoiceResponse()

    if api_version == "v1":
        for language in ['de', 'en-gb']:
            resp.say(hotline_translation['error_message_api_version'][language], voice='woman', language=language)
    else:
        resp.redirect('/v1/hotline/error/api_version')

    return str(resp)


@app.route('/<api_version>/hotline/error/language', methods=['GET', 'POST'])
def route_hotline_error_language(api_version):
    # Error response in case an invalid api_version is requested

    resp = VoiceResponse()

    if api_version == "v1":
        for language in ['de', 'en-gb']:
            resp.say(hotline_translation['error_message_language'][language], voice='woman', language=language)
    else:
        resp.redirect('/v1/hotline/error/api_version')

    return str(resp)
