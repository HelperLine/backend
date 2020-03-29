
from flask_backend import helper_accounts_collection, status, zip_code_helpers_collection

from flask_backend.nosql_scripts.account_scripts import support_functions, email_verification, verify_register_form
from pymongo.errors import DuplicateKeyError

from flask_backend.secrets import TEST_EMAIL, TEST_PASSWORD, TEST_ZIP_CODE

import time


def add_helper_account(email, password, zip_code, country="Germany"):
    verification_status = verify_register_form.verify_register_form(email, password, zip_code, country)

    if verification_status["status"] == "ok":
        new_helper = {
            "email": email,
            "email_verified": False,
            "password": support_functions.hash_password(password),
            "zip_code": zip_code,
            "country": country
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

        # adding helper to zip-code-traffic
        zip_code_helpers_collection.update_one({"zip_code": zip_code}, {'$push': {'helpers': helper_id}})

        # TODO: Login and return email/api_key dict

        return status("ok")

    else:
        return verification_status


if __name__ == "__main__":
    t1 = time.time()
    print(add_helper_account(TEST_EMAIL, TEST_PASSWORD, TEST_ZIP_CODE))
    t2 = time.time()

    print(f"total: {t2 - t1} seconds")
    helper_accounts_collection.delete_many({})
    zip_code_helpers_collection.update_one({"zip_code": TEST_ZIP_CODE}, {'helpers': []})





