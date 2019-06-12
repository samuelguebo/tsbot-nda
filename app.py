# -*- coding: utf-8 -*-
#
# This project is based on the Toolforge Flask + OAuth WSGI tutorial
# It was tailored to fit the news of the Trust & Safety team
#
# Contributors: Samuel Guebo
# Licence: MIT
# Credit: The code-base is a fork of the Toolforge flask WSGI boilerplate
# as built in 2017 by Bryan Davis and other contributors

import flask
from flask import Response
from flask import url_for
import mwoauth
import os
import yaml
import requests


app = flask.Flask(__name__)


# Load configuration from YAML file
__dir__ = os.path.dirname(__file__)
app.config.update(
    yaml.safe_load(open(os.path.join(__dir__, 'config.yaml'))))


@app.route('/')
def index():
    greeting = app.config['GREETING']
    title = app.config['TITLE']
    description = app.config['DESCRIPTION']
    username = flask.session.get('username', None)
    return flask.render_template(
        'index.html', username=username, greeting=greeting,
        title=title, description=description)

@app.route('/user-contribs')
def user_contribs():
    """User contributions analysis.
    
    Call the MediaWiki server to get perform requests.
    Unauthorized users will be redirected to login page.
    """
    username = flask.session.get('username', None)
    if username:
        return flask.redirect(flask.url_for('index'))
    
    return flask.redirect(flask.url_for('contribs'))


@app.route('/query/<query>/<wiki>')
def wiki_query(query, wiki):
    """Endpoint for handling wiki queries to avoid X-Origin issues. """
    wikiurl = "https://" + wiki + "/w/api.php?action=query&" + query
    jsoncode = requests.get(wikiurl).content
    resp = Response(jsoncode, status=200,
                    mimetype='application/json')
    return resp
    
@app.route('/login')
def login():
    """Initiate an OAuth login.
    
    Call the MediaWiki server to get request secrets and then redirect the
    user to the MediaWiki server to sign the request.
    """
    consumer_token = mwoauth.ConsumerToken(
        app.config['CONSUMER_KEY'], app.config['CONSUMER_SECRET'])
    try:
        redirect, request_token = mwoauth.initiate(
            app.config['OAUTH_MWURI'], consumer_token)
    except Exception:
        app.logger.exception('mwoauth.initiate failed')
        return flask.redirect(flask.url_for('index'))
    else:
        flask.session['request_token'] = dict(zip(
            request_token._fields, request_token))
        return flask.redirect(redirect)


@app.route('/oauth-callback')
def oauth_callback():
    """OAuth handshake callback."""
    if 'request_token' not in flask.session:
        flask.flash(u'OAuth callback failed. Are cookies disabled?')
        return flask.redirect(flask.url_for('index'))

    consumer_token = mwoauth.ConsumerToken(
        app.config['CONSUMER_KEY'], app.config['CONSUMER_SECRET'])

    try:
        access_token = mwoauth.complete(
            app.config['OAUTH_MWURI'],
            consumer_token,
            mwoauth.RequestToken(**flask.session['request_token']),
            flask.request.query_string)

        identity = mwoauth.identify(
            app.config['OAUTH_MWURI'], consumer_token, access_token)    
    except Exception:
        app.logger.exception('OAuth authentication failed')
    
    else:
        flask.session['access_token'] = dict(zip(
            access_token._fields, access_token))
        flask.session['username'] = identity['username']

    return flask.redirect(flask.url_for('index'))


@app.route('/logout')
def logout():
    """Log the user out by clearing their session."""
    flask.session.clear()
    return flask.redirect(flask.url_for('index'))