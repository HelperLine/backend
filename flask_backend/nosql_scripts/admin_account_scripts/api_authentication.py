
from pymongo import DeleteMany, InsertOne

from flask_backend.nosql_scripts.helper_account_scripts import support_functions
from flask_backend import status, admin_api_keys_collection, admin_accounts_collection


# ---------------------------------------------------------------------------------------------------------------------


def admin_create_new_api_key(email):
    api_key = support_functions.generate_random_key(length=64)

    operations = [
        DeleteMany({"email": email}),
        InsertOne({"email": email, "api_key": api_key})
    ]
    admin_api_keys_collection.bulk_write(operations, ordered=True)

    return api_key


def admin_delete_api_key(email):
    admin_api_keys_collection.delete_many({"email": email})


# ---------------------------------------------------------------------------------------------------------------------


def admin_login_password(email, password):
    admin_account = admin_accounts_collection.find_one({"email": email})

    if admin_account is not None:
        if support_functions.check_password(password, admin_account["hashed_password"]):
            api_key = admin_create_new_api_key(email)
            return status("ok", email=email, api_key=api_key)

    return {"status": "invalid email/password"}


def admin_login_api_key(email, api_key, new_api_key=False):
    admin_api_key = admin_api_keys_collection.find_one({"email": email})

    if admin_api_key is not None:
        if api_key == admin_api_key["api_key"]:
            if new_api_key:
                api_key = admin_create_new_api_key(email)

            return status("ok", email=email, api_key=api_key)

    return {"status": "invalid email/api_key"}


# ---------------------------------------------------------------------------------------------------------------------


def admin_logout(email, api_key):
    helper_api_key = admin_api_keys_collection.find_one({"email": email})
    if api_key == helper_api_key["api_key"]:
        admin_delete_api_key(email)


