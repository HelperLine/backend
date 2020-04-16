
from cerberus import Validator
from flask_backend.support_functions import formatting


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


filter_schema = {
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
    'switch_online_after_call': {
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


def validate(filter_document, validator_object):
    if validator_object.validate(filter_document):
        return formatting.status('ok')
    else:
        error_message = f'validation error: {str(validator_object.errors)}'
        return formatting.status(error_message)

 
filter_validator = Validator(filter_schema)
forward_validator = Validator(forward_schema)


def validate_filter(filter_document):
    return validate(filter_document, filter_validator)


def validate_forward(forward_document):
    return validate(forward_document, forward_validator)


if __name__ == '__main__':
    filter_example = {
        'call_type': {
            'only_local': True,
            'only_global': True,
        },
        'language': {
            'german': False,
            'english': False,
        },
    }

    forward_example = {
        'online': False,
        'schedule_active': False,
        'schedule': [
            {'from': 13, 'to': 27},
            {'from': 12, 'to': 10},
        ],
    }

    print(validate_filter(filter_example))
    print(validate_forward(forward_example))
