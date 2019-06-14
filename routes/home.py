import flask
from flask import Blueprint, render_template
from flask import Flask
app = Flask(__name__)

home = Blueprint('home', __name__)

@home.route('/')
def index():

	username = flask.session.get('username', None)
	return flask.render_template(
	'index.html', username=username)