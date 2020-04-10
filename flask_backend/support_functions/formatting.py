
def status(text, **kwargs):
    status_dict = {'status': text}
    status_dict.update(kwargs)
    return status_dict


def datetime_to_string(datetime_object):
    return datetime_object.strftime("%d.%m.%y, %H:%M")
