import pymongo
import pharos

_client = None

def _get_client():
    global _client
    if not _client:
        _client = pymongo.MongoClient(
            pharos.get_preference(pharos.DOCKER_BRIDGE), 
            pharos.get_preference(pharos.MONGOS_PORT))
    return _client

def get_hosts():
    col = _get_client().pharos.node
    return list(col.find())
