from flask import Flask
import os
import yaml
from tinydb import TinyDB
from datetime import timedelta
from datetime import datetime


APP_ROOT = os.path.dirname(os.path.abspath(__file__))
APP_STATIC = os.path.join(APP_ROOT, 'static')
app = Flask(__name__)

# Load configuration from YAML file
__dir__ = os.path.dirname(__file__)
app.config.update(
    yaml.safe_load(open(APP_ROOT + '/config.yaml')))


def before_request():
    """Data rentention: reset the DB every two days"""
    try:

        db = get_db()
        searches = db.all()

        for search in searches:
            timestamp = datetime.strptime(search['timestamp'],
                                          '%Y-%m-%d %H:%M:%S')
            # Delete data older than 48 hours
            if timestamp <= datetime.now() - timedelta(days=2):
                db.remove(doc_ids=[search.doc_id])
        pass

    except Exception as e:
        print(e)
        pass


def get_db():
    """DB object to be used independently."""

    # setting the tinydb location
    db = TinyDB('database/db.json')

    return db
