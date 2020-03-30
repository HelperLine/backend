
from flask_backend import helper_accounts_collection

from flask_backend.nosql_scripts.helper_account_scripts import support_functions
from flask_backend.nosql_scripts.admin_account_scripts import api_authentication

from flask_backend.secrets import ADMIN_EMAIL, ADMIN_PASSWORD

import time


def add_admin_account(email, password):
    new_admin = {
        "username": email,
        "hashed_password": support_functions.hash_password(password),
    }
    return api_authentication.admin_login_password(email, password)


if __name__ == "__main__":
    add_admin_account(ADMIN_EMAIL, ADMIN_PASSWORD)
