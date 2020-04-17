
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_restful import Api

import os
import certifi
from google.cloud import datastore
from pymongo import MongoClient

from flask_backend.support_functions.formatting import status




# Set correct SSL certificate
os.environ['SSL_CERT_FILE'] = certifi.where()




if os.getenv("ENVIRONMENT") != "production":
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "service-account.json"

client = datastore.Client()
raw_query_result = list(client.query(kind='Secrets').fetch())
for entity in raw_query_result:
    os.environ[entity["name"]] = entity["value"]

MONGODB_WRITE_CONNECTION_STRING = os.getenv('MONGODB_WRITE_CONNECTION_STRING')
SECRET_KEY = os.getenv('SECRET_KEY')
BCRYPT_SALT = os.getenv('BCRYPT_SALT')
GCP_API_KEY = os.getenv('GCP_API_KEY')
SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
BACKEND_URL = os.getenv('BACKEND_URL')
FRONTEND_URL = os.getenv('FRONTEND_URL')




# Connect to database and collections
client = MongoClient(MONGODB_WRITE_CONNECTION_STRING)

admin_database = client.get_database('admin_database')
admin_accounts_collection = admin_database['accounts']
admin_api_keys_collection = admin_database['api_keys']

helper_database = client.get_database('helper_database')
helper_accounts_collection = helper_database['accounts']
helper_api_keys_collection = helper_database['api_keys']
email_tokens_collection = helper_database['email_tokens']
phone_tokens_collection = helper_database['phone_tokens']
helper_behavior_collection = helper_database['behavior']

call_database = client.get_database('call_database')
calls_collection = call_database['calls']
caller_accounts_collection = call_database['callers']
call_queue = call_database['queue']

zip_code_dataset = client.get_database('zip_code_dataset')
zip_codes_collection = zip_code_dataset['zip_codes_germany']




app = Flask(__name__)

# Cookies (e.g. user/admin login) are stored for 7 days
app.config['REMEMBER_COOKIE_DURATION'] = 60 * 60 * 24 * 7
app.config['SECRET_KEY'] = SECRET_KEY

cors = CORS(app)
bcrypt = Bcrypt(app)
api = Api(app)


from flask_backend.backend_routes.default_routes import default_routes
from flask_backend.backend_routes.hotline_routes import hotline_routes, hotline_error_routes
from flask_backend.backend_routes.authentication_routes import authentication_login_routes, authentication_logout_routes
from flask_backend.backend_routes.database_routes import database_resources_routes, database_fetch_routes
from flask_backend.backend_routes.settings_routes import settings_resources_routes
from flask_backend.backend_routes.verification_routes import verification_email_routes, verification_phone_form_routes, verification_phone_hotline_routes
