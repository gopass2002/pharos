# default modules
import json
import socket

# 3rd party modules
import flask
from flask import request
import requests
import pymongo
import docker

# pharos modules
import pharos.config as config

from . import (
    InvalidUsage,
    app
)

class AlreadyExists(InvalidUsage):
    def __init__(self, record, status_code=None, payload=None):
        InvalidUsage.__init__(self, 'Already Exists: ' + repr(record), status_code, payload)

class NotFoundRecord(InvalidUsage):
    def __init__(self, recode, status_code=None, payload=None):
        InvalidUsage.__init__(self, 'Not Found Record: ' + repr(recode), status_code, payload)

class StorageIsNotAvailable(InvalidUsage):
    def __init__(self, storage, status_code=None, payload=None):
        InvalidUsage.__init__(self, 'Storage is not available: ' + storage, status_code, payload)


def get_containers_count(host, port):
    'return count of containers if docker daemon is available'
    docker_client = docker.Client('tcp://%s:%i' % (host, port), timeout=1)
    try:
        return len(docker_client.containers())
    except requests.exceptions.ConnectionError:
        return -1

def check_storage_status(host, port):
    'check storage is available'
    # TODO check storage type
    try:
        c = pymongo.MongoClient('%s:%i' % (host, port), connectTimeoutMS=1000)
        return True
    except pymongo.errors.ConnectionFailure:
        return False

@app.route('/nodes', methods=['GET', 'POST', 'DELETE'])
def list_node():
    try:
        c = pymongo.MongoClient('localhost:27017') 
    except pymongo.errors.ConnectionFailure:
        raise StorageIsNotAvailable('MongoDB', status_code=500)
    if request.method == 'POST':
        # insert new recode
        req = json.loads(request.data)
        res = c.pharos.nodes.find_one(req)
        if res:
            # return conflict current recode: 409
            raise AlreadyExists(res, status_code=409)
        res = c.pharos.nodes.insert(req)
        if not res:
            pass
        req['_id'] = str(req.pop('_id'))
        return flask.jsonify(req)
    elif request.method == 'DELETE':
        req = json.loads(request.data)
        res = c.pharos.nodes.find_one(req)
        if not res:
            raise NotFoundRecord(res, status_code=404)
        c.pharos.nodes.remove(res)
        res['_id'] = str(res.pop('_id'))
        return flask.jsonify(res)

    nodes = list(c.pharos.nodes.find())
    res = {'n': len(nodes)}
    for node in nodes:
        node['_id'] = str(node.pop('_id'))
        host = node['host']
        # health check
        node['containers'] = get_containers_count(host, config.get_preference(config.DOCKER_REMOTE_API_PORT))
        node['storage'] = check_storage_status(host, config.get_preference(config.MONGOS_PORT))
    res['nodes'] = nodes
    return flask.jsonify(res)

@app.route('/nodes/<host>/metrics', methods=['GET'])
def metrics_node(host=None):
    c = pymongo.MongoClient('%s:%i' % (socket.gethostname(), config.get_preference(config.MONGOS_PORT)))
    q = {'Host': host}
    res = c.pharos.node_metrics.find_one(q)
    res['_id'] = str(res.pop('_id'))
    return flask.jsonify(res)

