
from flask_backend import app
from flask_backend.support_functions import formatting
from flask import redirect


@app.route("/", methods=["GET"])
def route_index():
    return "<p>This is the helperline backend." \
           "<br/><br/>" \
           "See <a href='https://helperline.io/' target='_blank'>helperline.io</a> for more." \
           "<br/><br/>" \
           "See the API documentation <a href='/v1/docs' target='_blank'>here</a>.</p>"



@app.route("/<api_version>/docs")
def route_docs(api_version):

    if api_version == "v1":
        return redirect("https://app.swaggerhub.com/apis-docs/helperline/backend/1.0")

    else:
        return formatting.status("api_version invalid")
