"""
This part of the flask app servers the main http requests
"""
from Flask import Blueprint, render_template

bp = Blueprint("main", __name__, "/")


@bp.route("/index")
@bp.route("/index.html")
@bp.route("/")
def index():
    return render_template("index.html")
