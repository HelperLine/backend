
from flask_backend import app


@app.route("/", methods=["GET"])
def route_index():
    return "<p>This is the helperline backend. See <a href=" \
           "'https://helperline.io/'>helperline.io</a> for more.</p>"

