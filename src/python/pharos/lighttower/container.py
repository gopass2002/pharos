# default modules
import json

# 3rd party modules
import flask
import pymongo

# pharos modules
from . import app
from . import get_mongo_client

import pharos.config as config

@app.route('/containers')
def list_containers():
    args = flask.request.args
    
    mongos = get_mongo_client()
    collection = mongos.pharos.containers
    
    q = {}
    if 'host' in args:
        q['Host'] = args['host']
    status_all = False
    if 'all' in args:
        if args['all'] == 'true':
            status_all = True

    print q
    containers = list(collection.find(q))
    response = []
    for container in containers:
        status = container['State']['Running']
        if status_all or status:
            container['_id'] = str(container.pop('_id'))
            response.append(container)

    return flask.jsonify({'containers': response, 'n': len(response)})

@app.route('/containers/<container_id>/metrics', methods=['GET'])
def get_container_metrics(container_id=None):
    mongos = get_mongo_client()
    collection = mongos.pharos.container_metrics
    q = {'Id' : {'$regex' : container_id + '.*'}}
    container = collection.find_one(q)
    if not container:
        # TODO: handle exception
        pass
    container['_id'] = str(container.pop('_id'))
    return flask.jsonify(container)
