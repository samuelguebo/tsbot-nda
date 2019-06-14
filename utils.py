from flask import Flask
import flask
import os, yaml

APP_ROOT = os.path.dirname(os.path.abspath(__file__))   # refers to application_top
APP_STATIC = os.path.join(APP_ROOT, 'static')
app = Flask(__name__)

# Load configuration from YAML file
__dir__ = os.path.dirname(__file__)
app.config.update(
    yaml.safe_load(open(APP_ROOT + '/config.yaml')))


def has_credentials():
    """Verify wether logged in user has adequate credentials"""
    username = flask.session.get('username', None)
    usergroup = flask.session.get('usergroup', None)
    if username and usergroup=="wmf-supportsafety":
        return True
    return False