import flask
from flask import Blueprint
from flask import Flask
import os
import re

app = Flask(__name__)

home = Blueprint('home', __name__)


@home.route('/')
def index():
    username = flask.session.get('username', None)
    return flask.render_template('index.html', username=username)

@home.route('/public/<path:path>')
def public(path):
    # redirect / to index.html
    if not re.match(r"^.*\.[^\\]+$", path):
        path += '/index.html'
        return flask.redirect((path))

    public_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../public")
    full_path = public_dir + "/" + path
    print("full_path:" + full_path)
    data = open(full_path).read()  
    return data