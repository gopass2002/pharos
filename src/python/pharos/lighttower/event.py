# default modules
import json

# 3rd party modules
import flask
import pymongo

# pharos modules
from . import app
from . import get_mongo_client

import pharos.config as config

@app.route('/events')
def list_events():
    args = flask.request.args

    mongos = get_mongo_client()
    collection = mongos.pharos.events

    q = {}
    if 'status' in args:
        q['status'] = args['status']
    if 'id' in args:
        q['id'] = {'$regex' : args['id'] + '.*'}
    
    events = list(collection.find(q))

    for event in events:
        event['_id'] = str(event.pop('_id'))
    
    return flask.jsonify({'events': events, 'n': len(events)})
