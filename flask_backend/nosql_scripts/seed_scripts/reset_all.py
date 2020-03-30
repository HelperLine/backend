
from flask_backend import admin_accounts_collection, caller_accounts_collection, helper_accounts_collection

from flask_backend import calls_collection, agent_behavior_collection

from flask_backend import zip_code_callers_collection, zip_code_helpers_collection, zip_code_calls_collection

from flask_backend import helper_api_keys_collection, admin_api_keys_collection, email_tokens_collection


def delete_all():
    admin_accounts_collection.delete_many({})
    caller_accounts_collection.delete_many({})
    helper_accounts_collection.delete_many({})

    calls_collection.delete_many({})
    agent_behavior_collection.delete_many({})

    zip_code_helpers_collection.update_many({}, {"$set": {"helpers": []}})
    zip_code_callers_collection.update_many({}, {"$set": {"callers": []}})
    zip_code_calls_collection.update_many({}, {"$set": {"pending_calls": []}})

    helper_api_keys_collection.delete_many({})
    admin_api_keys_collection.delete_many({})
    email_tokens_collection.delete_many({})


if __name__ == "__main__":
    delete_all()


