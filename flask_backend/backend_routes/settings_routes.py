
from flask_backend import api

from flask_backend.restful_resources.rest_filter import RESTFilter


api.add_resource(RESTFilter, '/v1/settings/filter')
