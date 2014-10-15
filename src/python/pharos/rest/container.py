import flask
from pharos.rest import *
import json

@app.route('/containers')
def list_containers():
    return flask.jsonify('test')
