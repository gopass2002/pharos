# default modules
import json

# 3rd party modules
import flask
import pymongo

# pharos modules
from . import app
from . import get_mongo_client

from pharos.common import get_preference
from pharos.common import MONGOS_PORT

@app.route('/containers')
def list_containers():
    args = flask.request.args
    
    mongos = get_mongo_client()
    collection = mongos.pharos.node_metrics
    
    q = {}
    if 'host' in args:
        q['hostname'] = args['host']
    status_all = False
    if 'all' in args:
        if args['all'] == 'true':
            status_all = True

    print q
    nodes = list(collection.find(q))
    containers = []
    for node in nodes:
        hostname = node['hostname']
        for container in node['containers']:
            status = container['State']['Running']
            if status_all or status:
                container['hostname'] = hostname
                containers.append(container)

    return flask.jsonify({'containers': containers, 'n': len(containers)})

@app.route('/containers/<container_id>/metrics', methods=['GET'])
def get_container_metrics(container_id=None):
    mongos = get_mongo_client()
    collection = mongos.pharos.container_metrics
    q = {'Id' : {'$regex' : container_id + '.*'}}
    container = collection.find_one(q)
    container['_id'] = str(container.pop('_id'))
    return flask.jsonify(container)
