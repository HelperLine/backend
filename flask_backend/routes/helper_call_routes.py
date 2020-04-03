
from flask_backend import app, status


@app.route("/backend/calls/accept", methods=["POST"])
def accept_call_route():
    return status("no new calls")


@app.route("/backend/calls/fulfill", methods=["POST"])
def fulfill_call_route():
    return status("ok")


@app.route("/backend/calls/reject", methods=["POST"])
def reject_call_route():
    return status("ok")







