
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

account_database = client.get_database('account_database')
admin_accounts_collection = account_database['admin_accounts']
helper_accounts_collection = account_database['helper_accounts']

call_database = client.get_database('call_database')
calls_collection = call_database['calls']
caller_accounts_collection = call_database['caller_accounts']
helper_behavior_collection = call_database['helper_behavior']

zip_code_dataset = client.get_database('zip_code_dataset')
zip_codes_collection = zip_code_dataset['zip_codes_germany']

token_database = client.get_database('token_database')
helper_api_keys_collection = token_database['helper_api_keys']
admin_api_keys_collection = token_database['admin_api_keys']
email_tokens_collection = token_database['email_tokens']
phone_tokens_collection = token_database['phone_tokens']

queue_database = client.get_database('queue_database')
call_queue = queue_database['call_queue']




app = Flask(__name__)

# Cookies (e.g. user/admin login) are stored for 7 days
app.config['REMEMBER_COOKIE_DURATION'] = 60 * 60 * 24 * 7
app.config['SECRET_KEY'] = SECRET_KEY

cors = CORS(app)
bcrypt = Bcrypt(app)
api = Api(app)


from flask_backend.backend_routes import default_routes, helper_routes, call_routes, hotline_routes

if __name__ == '__main__':
    print(status('ok', api_key='1234567'))
