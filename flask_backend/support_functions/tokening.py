
from flask_backend import bcrypt, BCRYPT_SALT
from flask_backend.database_scripts.authentication_scripts import helper_authentication, admin_authentication
from flask_backend.support_functions import formatting

import random


def generate_random_key(length=32, numeric=False, existing_tokens=()):
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

    # Brute force generate random keys as long as key is not unique
    while random_key in existing_tokens:
        random_key = random_key[1:] + random.choice(possible_characters)

    return random_key


def hash_password(password):
    return bcrypt.generate_password_hash(password + BCRYPT_SALT).decode('UTF-8')


def check_password(password, hashed_password):
    return bcrypt.check_password_hash(hashed_password, password + BCRYPT_SALT)


def check_helper_api_key(params_dict, new_api_key=False):
    email = params_dict['email']
    api_key = params_dict['api_key']

    if email is not None and api_key is not None:
        return helper_authentication.helper_login_api_key(email, api_key, new_api_key=new_api_key)
    else:
        return formatting.status('email/api_key missing')


def check_admin_api_key(params_dict, new_api_key=False):
    email = params_dict['email']
    api_key = params_dict['api_key']

    if email is not None and api_key is not None:
        return admin_authentication.admin_login_api_key(email, api_key, new_api_key=new_api_key)
    else:
        return formatting.status('email/api_key missing')
