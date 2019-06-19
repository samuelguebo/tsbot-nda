from flask import Blueprint, Response, request
import flask
import json
from utils import get_db
from datetime import datetime

contribs = Blueprint('contribs', __name__)


@contribs.route('/contribs')
def index():
    """User contributions analysis.

    Call the MediaWiki server to get perform requests.
    Unauthorized users will be redirected to login page.
    """

    return flask.render_template('contribs.html')


@contribs.route('/contribs/reverts')
def reverts():
    """Find reverted edits"""
    operation = "revert"
    return flask.render_template('contribs.html', operation=operation)


@contribs.route('/contribs/save', methods=["PUT"])
def save():
    """Save the user contributions collected into database"""

    req_data = request.get_json()
    username = flask.session.get('username', "African Hope")

    # try:
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
        return Response(result_json, status=200, mimetype='application/json')
    # except:
        # pass

    return Response({}, status=404, mimetype='application/json')


@contribs.route('/contribs/view/<id>')
def view(id):
    """Display a search that was previously saved"""

    db = get_db()
    search = db.get(doc_id=int(id))

    return flask.render_template("contribs.html", search=search)


@contribs.route('/contribs/list')
def list():
    """List all searches performed and saved previously"""

    db = get_db()
    searches = db.all()

    return flask.render_template("list.html", searches=searches)


@contribs.route('/contribs/delete/<id>')
def delete(id):
    """Delete the user contributions collected into database"""

    notification = {"status": "error",
                    "text": "Deletion failed, an error occured."
                    }
    # Make sure item exists
    db = get_db()
    id = int(id)
    search = db.get(doc_id=id)

    if(search):
        db.remove(doc_ids=[id])
        notification['status'] = "success"
        notification['text'] = "The search was successfulled deleted."

    searches = db.all()

    return flask.render_template('list.html', searches=searches,
                                 notification=notification)

    # except:
    # pass

    return Response({}, status=404,
                    mimetype='application/json')
