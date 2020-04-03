
from flask_backend import app
from flask import render_template


@app.errorhandler(404)
def page_not_found(e):
    # Every url not associated with the backend is directly
    # routed to the frontend (which will also handle 404's)

    return render_template("index.html")

