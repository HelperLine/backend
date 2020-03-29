
from flask_backend import bcrypt, BCRYPT_SALT
import random


def generate_random_key(length=32):
    possible_characters = []

    # Characters '0' through '9'
    possible_characters += [chr(x) for x in range(48, 58)]

    # Characters 'A' through 'Z'
    possible_characters += [chr(x) for x in range(65, 91)]

    # Characters 'a' through 'z'
    possible_characters += [chr(x) for x in range(97, 123)]

    random_key = ""

    for i in range(length):
        random_key += random.choice(possible_characters)

    return random_key


def hash_password(password):
    return bcrypt.generate_password_hash(password + BCRYPT_SALT).decode('UTF-8')


def check_password(password, hashed_password):
    return bcrypt.check_password_hash(hashed_password, password + BCRYPT_SALT)
