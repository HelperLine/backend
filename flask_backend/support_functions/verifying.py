

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
    number_check = letter_check = False

    if len(password) < 8:
        return False

    for letter in password:
        if (letter in NUMBERS):
            number_check = True
        elif (letter in UPPER_CASE_LETTERS) or (letter in LOWER_CASE_LETTERS):
            letter_check = True

    return (number_check and letter_check)


def verify_zip_code_format(zip_code):

    if len(zip_code) != 5:
        return False

    for digit in zip_code:
        if digit not in NUMBERS:
            return False

    return True


def verify_country_format(country):
    # List of supported countries
    return country in ['Germany', 'Deutschland']
