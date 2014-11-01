
import pymongo
import flask

from pharos.common import get_preference
from pharos.common import MONGOS_PORT

__VIEWS__ = ['node', 'container']
app = flask.Flask(__name__)
_mongos = None

class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['return_code'] = self.status_code
        rv['message'] = self.message
        return rv

@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = flask.jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


def get_mongo_client():
    global _mongos

    if not _mongos:
        _mongos = pymongo.MongoClient('localhost', get_preference(MONGOS_PORT))
    return _mongos
