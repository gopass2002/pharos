import flask
from . import app

@app.route('/containers')
def list_containers():
    return flask.jsonify('test')
