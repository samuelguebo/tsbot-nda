# -*- coding: utf-8 -*-
#
# This project is based on the Toolforge Flask + OAuth WSGI tutorial
# It was tailored to fit the news of the Trust & Safety team
#
# Contributors: Samuel Guebo
# Licence: MIT
# Credit: The code-base is a fork of the Toolforge flask WSGI boilerplate
# as built in 2017 by Bryan Davis and other contributors
#
# This project is based on the Toolforge Flask + OAuth WSGI tutorial
# It was tailored to fit the news of the Trust & Safety team
#
# Contributors: Samuel Guebo
# Licence: MIT
# Credit: The code-base is a fork of the Toolforge flask WSGI boilerplate
# as built in 2017 by Bryan Davis and other contributors
import flask
from flask import Flask
from routes.auth import auth
from routes.home import home
from routes.contribs import contribs
import yaml, os

app = Flask(__name__)
app.register_blueprint(auth)
app.register_blueprint(home)
app.register_blueprint(contribs)

# Load configuration from YAML file
__dir__ = os.path.dirname(__file__)
app.config.update(
    yaml.safe_load(open(os.path.join(__dir__, 'config.yaml'))))

@app.context_processor
def inject_user():
    """Injecting variables in all templates"""
    greeting = app.config['GREETING']
    title = app.config['TITLE']
    description = app.config['DESCRIPTION']
    usergroup = flask.session.get('usergroup', None)
    return dict(greeting=greeting,title=title, 
                description=description, usergroup=usergroup)
