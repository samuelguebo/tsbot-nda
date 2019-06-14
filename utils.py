from flask import Flask
import flask
import os
import yaml
from flask import request

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
APP_STATIC = os.path.join(APP_ROOT, 'static')
app = Flask(__name__)

# Load configuration from YAML file
__dir__ = os.path.dirname(__file__)
app.config.update(
    yaml.safe_load(open(APP_ROOT + '/config.yaml')))


@app.before_request
def before_request():
    """Protecting non-public routes"""

    allowed_routes = ["home.index", "auth.login",
                      "auth.oauth_callback", "auth.logout"
                      ]
    if has_credentials() is False and request.endpoint not in allowed_routes:
        return flask.redirect(flask.url_for('home.index'))
    else:
        pass


def has_credentials():
    """Verify wether logged in user has adequate credentials"""
    username = flask.session.get('username', None)
    usergroup = flask.session.get('usergroup', None)
    if username and usergroup == "wmf-supportsafety":
        return True
    return False
