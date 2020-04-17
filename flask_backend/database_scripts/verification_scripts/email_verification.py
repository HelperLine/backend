
from flask_backend import SENDGRID_API_KEY, BACKEND_URL, email_tokens_collection, helper_accounts_collection
from flask_backend.support_functions import tokening, formatting

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import *
from pymongo import DeleteMany, InsertOne
from bson import ObjectId


def send(email, verification_token):
    message = Mail(
        from_email='verify@helperline.io',
        to_emails=email,
        subject='Verify your account!',
        html_content=f'<h2>Welcome to HelperLine!</h2>' +
                     f'<p>Please verify this email address: <a href=\'{BACKEND_URL}verification/v1' +
                     f'/email/{verification_token}\'>Verification Link</a></p>' +
                     f'<p>If you have not signed up for our service, you can just ignore this email</p>' +
                     f'<p>Best,<br/>The HelperLine Team</p>'
    )
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        return formatting.status('ok')
    except Exception as e:
        print(e)
        return formatting.status('email sending failed')


def verify(verification_token):
    record = email_tokens_collection.find_one({'token': verification_token})
    if record is not None:
        helper_accounts_collection.update_one({'_id': record['helper_id']}, {'$set': {'email_verified': True}})
        email_tokens_collection.delete_many({'helper_id': record['helper_id']})


def trigger(email):
    # this function can be used for the initial send as well as resending

    helper_account = helper_accounts_collection.find_one({'email': email})

    if helper_account['email_verified']:
        return formatting.status('email already verified')

    # Generate new token
    verification_token = tokening.generate_random_key(length=64)
    helper_id = ObjectId(helper_account["_id"])

    # Create new token record
    record = {'helper_id': helper_id, 'token': verification_token}
    operations = [
        DeleteMany({'helper_id': helper_id}),
        InsertOne(record)
    ]
    email_tokens_collection.bulk_write(operations, ordered=True)

    # Trigger token-email
    return send(email, verification_token)


if __name__ == '__main__':
    # trigger_email_verification('1402', TEST_EMAIL)
    # email_tokens_collection.delete_many({})

    # confirm_email('iu694Wfs8p7zVggbWeuLIPXplEhQoMHMXeDriOhMl0WRfSQSGhgDzLC0BIsJm32s')

    pass
