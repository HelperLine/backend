from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import *

from flask_backend import SENDGRID_API_KEY, BACKEND_URL, status, email_tokens_collection, helper_accounts_collection
from flask_backend.nosql_scripts.account_scripts import support_functions

from flask_backend.secrets import TEST_EMAIL

from pymongo import DeleteMany, InsertOne


def send_verification_mail(email, verification_token):
    message = Mail(
        from_email='verify@hilfe-am-ohr.de',
        to_emails=email,
        subject='Verify your account!',
        html_content=f'Please verify: <a href=\'{BACKEND_URL}backend/email/verify/{verification_token}\'>Verification Link</a>')
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        return status("ok")
    except Exception as e:
        print(e)
        return status("email sending failed")


def confirm_email(verification_token):
    record = email_tokens_collection.find_one({"token": verification_token})
    if record is not None:
        helper_accounts_collection.update_one({"_id": record["helper_id"]}, {"$set": {"email_verified": True}})
        email_tokens_collection.delete_many({"helper_id": record["helper_id"]})


def trigger_email_verification(helper_id, email):
    # Generate new token
    verification_token = support_functions.generate_random_key(length=64)

    # Create new token record
    record = {"helper_id": helper_id, "token": verification_token}
    operations = [DeleteMany({"helper_id": helper_id}), InsertOne(record)]
    email_tokens_collection.bulk_write(operations, ordered=True)

    # Trigger token-email
    return send_verification_mail(email, verification_token)


if __name__ == "__main__":
    # trigger_email_verification("1402", TEST_EMAIL)
    # email_tokens_collection.delete_many({})

    # confirm_email("iu694Wfs8p7zVggbWeuLIPXplEhQoMHMXeDriOhMl0WRfSQSGhgDzLC0BIsJm32s")

    pass


