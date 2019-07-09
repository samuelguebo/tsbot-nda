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
from routes.auth import auth
from routes.home import home
from routes.contribs import contribs
from routes.nda import nda

from utils import app

app.register_blueprint(auth)
app.register_blueprint(home)
app.register_blueprint(contribs)
app.register_blueprint(nda)


@app.context_processor
def inject_user():
    """Injecting variables in all templates"""
    greeting = app.config['GREETING']
    title = app.config['TITLE']
    description = app.config['DESCRIPTION']
    username = flask.session.get('username', None)
    usergroup = flask.session.get('usergroup', None)
    return dict(greeting=greeting, title=title, username=username,
                description=description, usergroup=usergroup)
