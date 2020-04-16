
from flask_backend import app, api
from flask_backend.support_functions import formatting

from flask_backend.restful_resources.rest_helper import RESTAccount


api.add_resource(RESTAccount, '/v1/database/account')


@app.route('/<api_version>/database/fetchall', methods=["GET"])
def route_database_fetchall(api_version):
    if api_version == "v1":
        pass
    else:
        return formatting.status("api_version invalid")


@app.route('/<api_version>/database/performance/<zip_code>', methods=["GET"])
def route_database_performance(api_version, zip_code):
    if api_version == "v1":
        pass
    else:
        return formatting.status("api_version invalid")
