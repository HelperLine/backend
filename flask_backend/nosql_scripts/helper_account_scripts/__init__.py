from flask_backend import helper_accounts_collection, status, helper_api_keys_collection, email_tokens_collection, \
    calls_collection, caller_accounts_collection

from flask_backend.nosql_scripts.helper_account_scripts import support_functions, email_verification, \
    verify_register_form, api_authentication
from pymongo.errors import DuplicateKeyError


import datetime

import time


def add_helper_account(email, password, zip_code, country="Germany"):
    verification_status = verify_register_form.verify_register_form(email, password, zip_code, country)

    print(verification_status)

    if verification_status["status"] == "ok":
        new_helper = {
            "email": email,
            "email_verified": False,
            "phone_number": "",
            "phone_number_verified": False,

            "hashed_password": support_functions.hash_password(password),
            "zip_code": zip_code,
            "country": country,

            "register_date": datetime.datetime.now().strftime("%d.%m.%y"),

            "filter_type_local": False,
            "filter_type_global": False,
            "filter_language_german": False,
            "filter_language_english": False,
        }

        try:
            # inserting helper document
            helper_id = helper_accounts_collection.insert_one(new_helper).inserted_id
        except DuplicateKeyError as e:
            # If two people sign up exactla at once
            # (verfication done but inserting fails for one)
            print(f"DuplicateKeyError: {e}")
            return status("email already taken")

        # Send verification email and add verification record
        email_verification.trigger_email_verification(helper_id, email)

        # login and return email/api_key dict
        return api_authentication.helper_login_password(email, password)

    else:
        return verification_status


def modify_helper_account(email, **kwargs):
    helper_account = helper_accounts_collection.find_one({"email": email})

    new_filter_type_local = new_filter_type_global = None

    if "filter_type_local" in kwargs and "filter_type_global" in kwargs:
        if not (kwargs["filter_type_local"] and kwargs["filter_type_global"]):
            new_filter_type_local = kwargs["filter_type_local"]
            new_filter_type_global = kwargs["filter_type_global"]

    if new_filter_type_local is None or new_filter_type_global is None:
        new_filter_type_local = helper_account["filter_type_local"]
        new_filter_type_global = helper_account["filter_type_global"]

    if "filter_language_german" in kwargs:
        new_filter_language_german = kwargs["filter_language_german"]
    else:
        new_filter_language_german = helper_account["filter_language_german"]

    if "filter_language_english" in kwargs:
        new_filter_language_english = kwargs["filter_language_english"]
    else:
        new_filter_language_english = helper_account["filter_language_english"]

    if "new_email" in kwargs:
        if (email != kwargs["new_email"]) and (helper_account["email_verified"]):
            return status("email already verified")
        else:
            if not verify_register_form.verify_email_format(kwargs["new_email"]):
                return status("email format invalid")
            else:
                new_email = kwargs["new_email"]
    else:
        new_email = email

    if "old_password" in kwargs and "new_password" in kwargs:
        if support_functions.check_password(kwargs["old_password"], helper_account["hashed_password"]):
            if not verify_register_form.verify_password_format(kwargs["new_password"]):
                return status("password format invalid")
            else:
                new_password = support_functions.hash_password(kwargs["new_password"])
        else:
            return status("old password invalid")
    else:
        new_password = helper_account["hashed_password"]

    if "zip_code" in kwargs:
        if not verify_register_form.verify_zip_code_format(kwargs["zip_code"]):
            return status("zip code format invalid")
        else:
            new_zip_code = kwargs["zip_code"]
    else:
        new_zip_code = helper_account["zip_code"]

    if "country" in kwargs:
        if not verify_register_form.verify_country_format(kwargs["country"]):
            return status("country invalid")
        else:
            new_country = kwargs["country"]
    else:
        new_country = helper_account["country"]

    if (new_email != helper_account["email"]) or (new_password != helper_account["hashed_password"]) or \
            (new_zip_code != helper_account["zip_code"]) or (new_country != helper_account["country"]) or \
            (new_filter_type_local != helper_account["filter_type_local"]) or \
            (new_filter_type_global != helper_account["filter_type_global"]) or \
            (new_filter_language_german != helper_account["filter_language_german"]) or \
            (new_filter_language_english != helper_account["filter_language_english"]):

        modified_helper_account = {
            "email": new_email,

            "hashed_password": new_password,
            "zip_code": new_zip_code,
            "country": new_country,

            "filter_type_local": new_filter_type_local,
            "filter_type_global": new_filter_type_global,
            "filter_language_german": new_filter_language_german,
            "filter_language_english": new_filter_language_english,
        }

        helper_accounts_collection.update_one({"email": email}, {"$set": modified_helper_account})

        if email != new_email:
            helper_api_keys_collection.update_one({"email": email}, {"$set": {"email": new_email}})
            email_tokens_collection.delete_one({"email": email})
            email_verification.trigger_email_verification(helper_account["_id"], new_email)

        # api_key remains the same
        response_dict = support_functions.get_all_helper_data(new_email)
    else:
        response_dict = support_functions.get_all_helper_data(email)

    return response_dict



if __name__ == "__main__":
    t1 = time.time()
    # print(add_helper_account(TEST_EMAIL, TEST_PASSWORD, TEST_ZIP_CODE))
    t2 = time.time()

    print(f"total: {t2 - t1} seconds")
    helper_accounts_collection.delete_many({})
