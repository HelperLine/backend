
from flask_backend import app, api
from flask_backend.database_scripts.call_scripts import call_scripts, forwarding
from flask_backend.support_functions import routing, tokening, formatting

from flask import request


from flask_backend.restful_resources.rest_call import RESTCall
api.add_resource(RESTCall, '/backend/v1/database/call')


@app.route('/backend/<api_version>/calls/accept', methods=['POST'])
def route_call_accept(api_version):

    if api_version == "v1":
        params_dict = routing.get_params_dict(request, print_out=True)


        authentication_result = tokening.check_admin_api_key(params_dict)
        if authentication_result["status"] != "ok":
            return authentication_result

        return call_scripts.accept_call(params_dict)

    else:
        return formatting.status("api_version invalid")


@app.route('/backend/<api_version>/forward/online', methods=['PUT'])
def route_call_set_online(api_version):

    if api_version == "v1":
        params_dict = routing.get_params_dict(request, print_out=True)

        authentication_result = tokening.check_admin_api_key(params_dict)
        if authentication_result["status"] != "ok":
            return authentication_result

        return forwarding.set_online(params_dict)

    else:
        return formatting.status("api_version invalid")


@app.route('/backend/<api_version>/forward/offline', methods=['PUT'])
def route_call_set_offline(api_version):

    if api_version == "v1":
        params_dict = routing.get_params_dict(request, print_out=True)

        authentication_result = tokening.check_admin_api_key(params_dict)
        if authentication_result["status"] != "ok":
            return authentication_result

        return forwarding.set_offline(params_dict)

    else:
        return formatting.status("api_version invalid")
