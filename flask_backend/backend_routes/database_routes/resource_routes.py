
from flask_backend import api

from flask_backend.restful_resources.rest_account import RESTAccount
from flask_backend.restful_resources.rest_call import RESTCall


api.add_resource(RESTAccount, '/v1/database/account')
api.add_resource(RESTCall, '/v1/database/call')
