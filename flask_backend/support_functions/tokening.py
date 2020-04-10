
from flask_backend import bcrypt, BCRYPT_SALT
from flask_backend.database_scripts.helper_scripts import api_authentication as helper_scripts
from flask_backend.database_scripts.admin_scripts import api_authentication as admin_scripts
from flask_backend.support_functions import formatting

import random


def generate_random_key(length=32, numeric=False):
    possible_characters = []

    # Characters '0' through '9'
    possible_characters += [chr(x) for x in range(48, 58)]

    if not numeric:
        # Characters 'A' through 'Z'
        possible_characters += [chr(x) for x in range(65, 91)]

        # Characters 'a' through 'z'
        possible_characters += [chr(x) for x in range(97, 123)]

    random_key = ''

    for i in range(length):
        random_key += random.choice(possible_characters)

    return random_key


def hash_password(password):
    return bcrypt.generate_password_hash(password + BCRYPT_SALT).decode('UTF-8')


def check_password(password, hashed_password):
    return bcrypt.check_password_hash(hashed_password, password + BCRYPT_SALT)


def check_helper_api_key(params_dict):
    email = params_dict['email']
    api_key = params_dict['api_key']

    if email is not None and api_key is not None:
        return helper_scripts.helper_login_api_key(email, api_key)
    else:
        return formatting.status('email/api_key missing')


def check_admin_api_key(params_dict):
    email = params_dict['email']
    api_key = params_dict['api_key']

    if email is not None and api_key is not None:
        return admin_scripts.admin_login_api_key(email, api_key)
    else:
        return formatting.status('email/api_key missing')
