
from datetime import datetime, timedelta, timezone


def get_current_time():
    return datetime.now(timezone(timedelta(hours=2)))


def datetime_to_string(datetime_object):
    return datetime_object.strftime("%d.%m.%y, %H:%M")
