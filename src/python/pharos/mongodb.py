import pymongo
from common import get_preference
from common import (DOCKER_BRIDGE, MONGOS_PORT)

_client = None

def _get_client():
    global _client
    if not _client:
        _client = pymongo.MongoClient(
            get_preference(DOCKER_BRIDGE), 
            get_preference(MONGOS_PORT))
    return _client

def get_hosts():
    col = _get_client().pharos.node
    return list(col.find())
