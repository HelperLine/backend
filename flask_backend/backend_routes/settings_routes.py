
from flask_backend import api
from flask_backend.restful_resources.rest_filter import RESTFilter
from flask_backend.restful_resources.rest_forward import RESTForward


api.add_resource(RESTFilter, '/v1/settings/filter')
api.add_resource(RESTForward, '/v1/settings/forward')
