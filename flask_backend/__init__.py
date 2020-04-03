from flask import Flask, request, redirect
import os

from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_restful import Api

try:
    from flask_backend.secrets import MONGODB_WRITE_CONNECTION_STRING
    from flask_backend.secrets import SECRET_KEY, BCRYPT_SALT, GCP_API_KEY, SENDGRID_API_KEY, BACKEND_URL
except Exception:

    # The secrets file will not be included in any repository and will
    # never leave this computer In production these values will be set
    # by environment variables

    MONGODB_WRITE_CONNECTION_STRING = os.getenv("MONGODB_WRITE_CONNECTION_STRING")
    SECRET_KEY = os.getenv("SECRET_KEY")
    BCRYPT_SALT = os.getenv("BCRYPT_SALT")
    GCP_API_KEY = os.getenv("GCP_API_KEY")
    SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
    BACKEND_URL = os.getenv("BACKEND_URL")


import os
import certifi
from pymongo import MongoClient

# Set correct SSL certificate
os.environ["SSL_CERT_FILE"] = certifi.where()


# Connect to database and collections
client = MongoClient(MONGODB_WRITE_CONNECTION_STRING)

account_database = client.get_database("account_database")
admin_accounts_collection = account_database["admin_accounts"]
caller_accounts_collection = account_database["caller_accounts"]
helper_accounts_collection = account_database["helper_accounts"]

call_database = client.get_database("call_database")
calls_collection = call_database["calls"]
helper_behavior_collection = call_database["helper_behavior"]

zip_code_dataset = client.get_database("zip_code_dataset")
zip_codes_collection = zip_code_dataset["zip_codes_germany"]

token_database = client.get_database("token_database")
helper_api_keys_collection = token_database["helper_api_keys"]
admin_api_keys_collection = token_database["admin_api_keys"]
email_tokens_collection = token_database["email_tokens"]

queue_database = client.get_database("queue_database")
call_queue = queue_database["call_queue"]


app = Flask(__name__)

# Cookies (e.g. user/admin login) are stored for 7 days
app.config['REMEMBER_COOKIE_DURATION'] = 60 * 60 * 24 * 7
app.config['SECRET_KEY'] = SECRET_KEY




cors = CORS(app)
bcrypt = Bcrypt(app)
api = Api(app)


def status(text, **kwargs):
    status_dict = {"status": text}
    status_dict.update(kwargs)
    return status_dict


@app.before_request
def before_request():
    if request.url.startswith('http://'):
        url = request.url.replace('http://', 'https://', 1)
        code = 301
        return redirect(url, code=code)


from flask_backend.routes import helper_account_routes, helper_call_routes, hotline_routes, react_routes


if __name__ == "__main__":
    print(status("ok", api_key="1234567"))




