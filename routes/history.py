from flask import Blueprint, Response, request
import flask
import json
from utils import get_db
from datetime import datetime

history = Blueprint('history', __name__)


@history.route('/history')
def index():
    """User contributions analysis.

    Call the MediaWiki server to get perform requests.
    Unauthorized users will be redirected to login page.
    """

    return flask.render_template('history.html')
