
from flask_backend import helper_accounts_collection, status
from flask_backend.support_functions import verifying


def verify_register_form(email, password, zip_code, country, new_account=True):
    if not verifying.verify_email_format(email):
        return status('email format invalid')

    if not verifying.verify_password_format(password):
        # Proper error message on client side
        return status('password format invalid')

    if not verifying.verify_zip_code_format(zip_code):
        return status('zip code format invalid')

    if not verifying.verify_country_format(country):
        return status('country invalid')


    if new_account and helper_accounts_collection.find_one({'email': email}) is not None:
        return status('email already taken')

    return status('ok')