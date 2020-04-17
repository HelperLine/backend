
def status(text, **kwargs):
    status_dict = {'status': text}
    status_dict.update(kwargs)
    return status_dict


language_conversion = {
    'de': 'german',
    'en-gb': 'english'
}

def twilio_language_to_string(twilio_language):
    if twilio_language not in language_conversion:
        return ''
    else:
        return language_conversion[twilio_language]


server_error_helper_record = status('server error', details='helper record not found after successful authentication')
