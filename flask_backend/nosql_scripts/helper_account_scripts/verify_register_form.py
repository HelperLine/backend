from flask_backend import helper_accounts_collection, status

NUMBERS = [chr(i) for i in range(48, 58)]
UPPER_CASE_LETTERS = [chr(i) for i in range(65, 91)]
LOWER_CASE_LETTERS = [chr(i) for i in range(97, 123)]


def verify_email_format(email):
    email = email.split('@')

    if len(email) != 2:
        return False

    if '.' not in email[1]:
        return False

    return True


def verify_password_format(password):
    number_check = upper_check = lower_check = sign_check = False

    if len(password) < 8:
        return False

    for letter in password:
        if letter in NUMBERS:
            number_check = True
        elif letter in UPPER_CASE_LETTERS:
            upper_check = True
        elif letter in LOWER_CASE_LETTERS:
            lower_check = True
        else:
            sign_check = True

    return (number_check and upper_check and lower_check and sign_check)


def verify_zip_code_format(zip_code):

    if len(zip_code) != 5:
        return False

    for digit in zip_code:
        if digit not in NUMBERS:
            return False

    return True


def verify_country_format(country):
    # List of supported countries
    return country in ["Germany"]


def verify_register_form(email, password, zip_code, country, new_account=True):
    if not verify_email_format(email):
        return status("email format invalid")

    if not verify_password_format(password):
        # Proper error message on client side
        return status("password format invalid")

    if not verify_zip_code_format(zip_code):
        return status("zip code format invalid")

    if not verify_country_format(country):
        return status("country invalid")


    if new_account and helper_accounts_collection.find_one({"email": email}) is not None:
        return status("email already taken")

    return status("ok")

