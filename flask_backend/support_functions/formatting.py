
def status(text, **kwargs):
    status_dict = {'status': text}
    status_dict.update(kwargs)
    return status_dict


server_error_helper_record = status('server error', details='helper record not found after successful authentication')
