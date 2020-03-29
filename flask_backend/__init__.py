from flask import Flask
import os

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_restful import Api

try:
    from flask_backend.secrets import SECRET_KEY, BCRYPT_SALT, GCP_API_KEY, SENDGRID_API_KEY, BACKEND_URL
except Exception:
    # The secrets file will not be included in any repository and will
    # never leave this computer In production these values will be set
    # by environment variables
    pass



app = Flask(__name__)

# Cookies (e.g. admin login) are stored for 7 days
app.config['REMEMBER_COOKIE_DURATION'] = 60 * 60 * 24 * 7




if os.getenv("SECRET_KEY") is not None:
    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
else:
    app.config['SECRET_KEY'] = SECRET_KEY

if os.getenv("BCRYPT_SALT") is not None:
    BCRYPT_SALT = os.getenv("BCRYPT_SALT")

if os.getenv("GCP_API_KEY") is not None:
    GCP_API_KEY = os.getenv("GCP_API_KEY")

if os.getenv("SENDGRID_API_KEY") is not None:
    SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")

if os.getenv("BACKEND_URL") is not None:
    BACKEND_URL = os.getenv("BACKEND_URL")




cors = CORS(app)
bcrypt = Bcrypt(app)
api = Api(app)
