
from cerberus import Validator
from flask_backend.support_functions import formatting

DIGITS = [chr(i) for i in range(48, 58)]
UPPER_CASE_LETTERS = [chr(i) for i in range(65, 91)]
LOWER_CASE_LETTERS = [chr(i) for i in range(97, 123)]


def check_filter_call_type(field, call_type_dict, error):
    true_count = 0
    for call_type in call_type_dict:
        true_count += 1 if call_type_dict[call_type] else 0
    if true_count > 1:
        error(field, 'select at most one call_type')


def check_filter_language(field, language_dict, error):
    true_count = 0
    for language in language_dict:
        true_count += 1 if language_dict[language] else 0
    if true_count == 0:
        error(field, 'select at least one language')


edit_filter_schema = {
    'call_type': {
        'type': 'dict',
        'required': True,
        'schema': {
            'only_local': {'type': 'boolean', 'required': True},
            'only_global': {'type': 'boolean', 'required': True}
        },
        'check_with': check_filter_call_type,
    },
    'language': {
        'type': 'dict',
        'required': True,
        'schema': {
            'german': {'type': 'boolean', 'required': True},
            'english': {'type': 'boolean', 'required': True}
        },
    },
}

accept_filter_schema = {
    'call_type': {
        'type': 'dict',
        'required': True,
        'schema': {
            'only_local': {'type': 'boolean', 'required': True},
            'only_global': {'type': 'boolean', 'required': True}
        },
        'check_with': check_filter_call_type,
    },
    'language': {
        'type': 'dict',
        'required': True,
        'schema': {
            'german': {'type': 'boolean', 'required': True},
            'english': {'type': 'boolean', 'required': True}
        },
        'check_with': check_filter_language,
    },
}


def check_forward_schedule_element(field, schedule_element, error):
    if schedule_element['from'] > schedule_element['to']:
        error(field, 'invalid schedule time (from_time > to_time)')


forward_schema = {
    'online': {
        'type': 'boolean',
        'required': True,
    },
    'stay_online_after_call': {
        'type': 'boolean',
        'required': True,
    },
    'schedule_active': {
        'type': 'boolean',
        'required': True,
    },
    'schedule': {
        'type': 'list',
        'required': True,
        'schema': {
            'type': 'dict',
            'schema': {
                'from': {'type': 'integer', 'required': True},
                'to': {'type': 'integer', 'required': True}
            },
            'check_with': check_forward_schedule_element,
        },
    },
}


def check_account_email(field, email, error):

    def invalid():
        error(field, 'email format invalid')
        return

    if type(email) == str:

        # Chained if statements because the latter depend on the previous
        # ones to be true in order not to throw an interpreter error

        email_parts = email.split('@')
        if len(email_parts) != 2:
            return invalid()

        if len(email_parts[0]) == 0:
            return invalid()

        if '.' not in email_parts[1]:
            return invalid()

        if '.' not in email_parts[1]:
            return invalid()

        email_domain_parts = email_parts[1].split('.')
        if any([(len(part) == 0) for part in email_domain_parts]):
            return invalid()


def check_account_password(field, password, error):
    if type(password) == str:
        no_digit_characters = not any([(c in DIGITS) for c in password])
        no_lower_characters = not any([(c in LOWER_CASE_LETTERS) for c in password])
        no_upper_characters = not any([(c in UPPER_CASE_LETTERS) for c in password])
        invalid_length = len(password) < 8

        if no_digit_characters or no_lower_characters or no_upper_characters or invalid_length:
            error(field, 'password format invalid')


def check_account_zip_code(field, zip_code, error):
    if type(zip_code) == str:
        non_digit_characters = any([(c not in DIGITS) for c in zip_code])
        invalid_length = len(zip_code) != 5

        if non_digit_characters or invalid_length:
            error(field, 'zip_code format invalid')


def check_account_country(field, country, error):
    if country not in ['Germany', 'Deutschland']:
        error(field, 'we currently offer our services only in Germany/Deutschland')


create_account_schema = {
    'email': {
        'type': 'string',
        'required': True,
        'check_with': check_account_email
    },
    'password': {
        'type': 'string',
        'required': True,
        'check_with': check_account_password
    },
    'zip_code': {
        'type': 'string',
        'required': True,
        'check_with': check_account_zip_code
    },
    'country': {
        'type': 'string',
        'required': True,
        'check_with': check_account_country
    },
}

edit_account_schema = {
    'new_email': {
        'type': 'string',
        'required': False,
        'check_with': check_account_email
    },
    'old_password': {
        'type': 'string',
        'required': False,
    },
    'new_password': {
        'type': 'string',
        'required': False,
        'check_with': check_account_password
    },
    'zip_code': {
        'type': 'string',
        'required': False,
        'check_with': check_account_zip_code
    },
    'country': {
        'type': 'string',
        'required': False,
        'check_with': check_account_country
    },
}


edit_call_schema = {
    'call_id': {
        'type': 'string',
        'required': True,
    },
    'action': {
        'type': 'string',
        'required': True,
        'allowed': ['reject', 'fulfill', 'comment'],
        'oneof': [{'dependencies': ['comment'], 'allowed': ['comment']}, {'allowed': ['reject', 'fulfill']}]
    },
    'comment': {
        'type': 'string',
        'dependencies': {'action': ['comment']}
    },
}


def validate(filter_document, validator_object):
    if validator_object.validate(filter_document):
        return formatting.status('ok')
    else:
        return formatting.status('validation error', errors=validator_object.errors)


accept_filter_validator = Validator(accept_filter_schema)
edit_filter_validator = Validator(edit_filter_schema)

forward_validator = Validator(forward_schema)
create_account_validator = Validator(create_account_schema)
edit_account_validator = Validator(edit_account_schema)
edit_call_validator = Validator(edit_call_schema)


def validate_accept_filter(params_dict):
    if "filter" not in params_dict:
        return formatting.status("filter missing")
    return validate(params_dict["filter"], accept_filter_validator)


def validate_edit_filter(params_dict):
    if "filter" not in params_dict:
        return formatting.status("filter missing")
    return validate(params_dict["filter"], edit_filter_validator)


def validate_forward(params_dict):
    if "forward" not in params_dict:
        return formatting.status("forward missing")
    return validate(params_dict["forward"], forward_validator)


def validate_create_account(params_dict):
    if "account" not in params_dict:
        return formatting.status("account missing")
    return validate(params_dict["account"], create_account_validator)


def validate_edit_account(params_dict):
    if "account" not in params_dict:
        return formatting.status("account missing")
    return validate(params_dict["account"], edit_account_validator)


def validate_edit_call(params_dict):
    if "call" not in params_dict:
        return formatting.status("call missing")
    return validate(params_dict["call"], edit_call_validator)


if __name__ == '__main__':

    edit_filter_example = {
        'call_type': {
            'only_local': True,
            'only_global': True,
        },
        'language': {
            'german': False,
            'english': False,
        },
    }
    print(validate_edit_filter({"filter": edit_filter_example}))


    forward_example = {
        'online': False,
        'schedule_active': False,
        'schedule': [
            {'from': 13, 'to': 27},
            {'from': 12, 'to': 10},
        ],
    }
    print(validate_forward({"forward": forward_example}))



    create_account_example = {
        'email': "a@b.c",
        'password': "aaaaaaA3",
        'zip_code': "80000",
        'country': "germany"
    }
    print(validate_create_account({"account": create_account_example}))



    edit_account_example = {
        'new_email': "a@b..c",
        'zip_code': "40000",
        'country': "Germany"
    }
    print(validate_edit_account({"account": edit_account_example}))



    edit_call_example_1 = {
        'call_id': 12,
        'action': "reject",
        'comment': "bla",
    }
    edit_call_example_2 = {
        'call_id': 12,
        'action': "reject",
    }
    edit_call_example_3 = {
        'call_id': 12,
        'action': "comment",
    }
    edit_call_example_4 = {
        'call_id': 12,
        'action': "comment",
        'comment': "bla",
    }
    print(validate_edit_call({"call": edit_call_example_1}))
    print(validate_edit_call({"call": edit_call_example_2}))
    print(validate_edit_call({"call": edit_call_example_3}))
    print(validate_edit_call({"call": edit_call_example_4}))
