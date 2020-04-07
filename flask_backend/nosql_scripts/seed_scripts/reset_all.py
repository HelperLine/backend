
from flask_backend import admin_accounts_collection, caller_accounts_collection, helper_accounts_collection

from flask_backend import calls_collection, helper_behavior_collection

from flask_backend import helper_api_keys_collection, admin_api_keys_collection, email_tokens_collection


def delete_all():
    admin_accounts_collection.delete_many({})
    caller_accounts_collection.delete_many({})
    helper_accounts_collection.delete_many({})

    calls_collection.delete_many({})
    helper_behavior_collection.delete_many({})

    helper_api_keys_collection.delete_many({})
    admin_api_keys_collection.delete_many({})
    email_tokens_collection.delete_many({})


if __name__ == '__main__':
    delete_all()
