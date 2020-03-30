
from pymongo import DeleteMany, InsertOne

from flask_backend.nosql_scripts.helper_account_scripts import support_functions
from flask_backend import status, helper_api_keys_collection, helper_accounts_collection


# ---------------------------------------------------------------------------------------------------------------------


def helper_create_new_api_key(email):
    api_key = support_functions.generate_random_key(length=64)

    operations = [
        DeleteMany({"email": email}),
        InsertOne({"email": email, "api_key": api_key})
    ]
    helper_api_keys_collection.bulk_write(operations, ordered=True)

    return api_key


def helper_delete_api_key(email):
    helper_api_keys_collection.delete_many({"email": email})


# ---------------------------------------------------------------------------------------------------------------------


def helper_login_password(email, password):
    helper_account = helper_accounts_collection.find_one({"email": email})

    if helper_account is not None:
        if support_functions.check_password(password, helper_account["hashed_password"]):
            api_key = helper_create_new_api_key(email)
            account = {
                "email_verified": helper_account["email_verified"],
                "zip_code": helper_account["zip_code"],
                "country": helper_account["country"]
            }
            return status("ok", email=email, api_key=api_key, account=account, calls={})

    return {"status": "invalid email/password"}


def helper_login_api_key(email, api_key, new_api_key=False):
    helper_api_key = helper_api_keys_collection.find_one({"email": email})

    if helper_api_key is not None:
        if api_key == helper_api_key["api_key"]:
            if new_api_key:
                api_key = helper_create_new_api_key(email)

            helper_account = helper_accounts_collection.find_one({"email": email})
            account = {
                "email_verified": helper_account["email_verified"],
                "zip_code": helper_account["zip_code"],
                "country": helper_account["country"]
            }
            return status("ok", email=email, api_key=api_key, account=account, calls={})

    return {"status": "invalid email/api_key"}


# ---------------------------------------------------------------------------------------------------------------------


def helper_logout(email, api_key):
    helper_api_key = helper_api_keys_collection.find_one({"email": email})
    if api_key == helper_api_key["api_key"]:
        helper_delete_api_key(email)


