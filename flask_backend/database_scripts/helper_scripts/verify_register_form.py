
from flask_backend import helper_accounts_collection
from flask_backend.support_functions import verifying, formatting


def verify_register_form(email, password, zip_code, country, new_account=True):
    if not verifying.verify_email_format(email):
        return formatting.status('email format invalid')

    if not verifying.verify_password_format(password):
        # Proper error message on client side
        return formatting.status('password format invalid')

    if not verifying.verify_zip_code_format(zip_code):
        return formatting.status('zip code format invalid')

    if not verifying.verify_country_format(country):
        return formatting.status('country invalid')


    if new_account and helper_accounts_collection.find_one({'email': email}) is not None:
        return formatting.status('email already taken')

    return formatting.status('ok')
