import flask
from flask import Blueprint, Response, request
import requests, json
from tinydb import TinyDB
from tinydb import Query
from datetime import datetime

contribs = Blueprint('contribs', __name__)

@contribs.route('/contribs')
def index():
    """User contributions analysis.
    
    Call the MediaWiki server to get perform requests.
    Unauthorized users will be redirected to login page.
    """
    username = flask.session.get('username', None)
    usergroup = flask.session.get('usergroup', None)
    """
    # Make sure only logged-in T&S staff can use this
    if username and usergroup=="wmf-supportsafety":
        return flask.render_template('contribs.html')
    
    return flask.redirect(flask.url_for('home.index'))
    """
    return flask.render_template('contribs.html')


@contribs.route('/contribs/save', methods=["POST"])
def save():
    """Save the user contributions collected into database"""
	
    req_data = request.get_json()
    username = flask.session.get('username', "African Hope")
    
    #try:
    # make sure data and username are legit 
    if len(req_data) > 0 and username:
        result = {
            "username": username,
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "contribs": req_data
        }
        
        db = get_db()
        result_id = db.insert(result)
        result_json = json.dumps({"result_id": result_id})
        return Response(result_json, status=200,
                            mimetype='application/json')
    #except:
        #pass
    
    return Response({}, status=404,
                        mimetype='application/json')

@contribs.route('/contribs/view/<id>')
def view(id):
    """Display a search that was previously saved"""
	
    db = get_db()
    search = db.get(doc_id=int(id))
    
    return flask.render_template("contribs.html", 
                                    search=search)


def get_db():

    """DB object to be used independently."""

    # setting the tinydb location
    db = TinyDB('database/db.json')

    return db