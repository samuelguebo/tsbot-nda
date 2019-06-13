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
import json
import mwoauth
import os
import yaml
import requests


app = flask.Flask(__name__)


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

@app.route('/')
def index():
    username = flask.session.get('username', None)
    return flask.render_template(
        'index.html', username=username)

@app.route('/user-contribs')
def user_contribs():
    """User contributions analysis.
    
    Call the MediaWiki server to get perform requests.
    Unauthorized users will be redirected to login page.
    """
    username = flask.session.get('username', None)
    usergroup = flask.session.get('usergroup', None)

    # Make sure only logged-in T&S staff can use this
    if username and usergroup and usergroup=="wmf-supportsafety":
        flask.render_template('contribs.html')
    
    return flask.redirect(flask.url_for('index'))


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
        usergroup = checkUserGroup(identity['username'])
        if usergroup == "wmf-supportsafety":
            flask.session['usergroup'] = usergroup 

    return flask.redirect(flask.url_for('index'))


@app.route('/logout')
def logout():
  """Log the user out by clearing their session."""
  flask.session.clear()
  return flask.redirect(flask.url_for('index'))

def checkUserGroup(username):
  """Check which rights a certain user possesses"""
  query = "list=users&ususers=" + username + "&usprop=groups&format=json"
  wikiurl = "https://meta.wikimedia.org/w/api.php?action=query&" + query
  
  jsonResult = requests.get(wikiurl).content
  groups = json.loads(jsonResult)['query']['users'][0]['groups']
  
  if "wmf-supportsafety" in groups:
    return "wmf-supportsafety"
  return "user"
  
