import os
import yaml

# configuration field headers
REMOTE_API_PORT = 'remote_api_port',
LIGHTTOWER_PORT = 'lighttower_port',
DOCKER_BRIDGE = 'docker_bridge'
DOCKER_PORT = 'docker_port'
DOCKER_API_VERSION = 'docker_api_version'
MONGOS_PORT = 'mongo_port'
CONFIG_FIELDS = (
    REMOTE_API_PORT, LIGHTTOWER_PORT,
    DOCKER_BRIDGE, DOCKER_PORT, DOCKER_API_VERSION, MONGOS_PORT,)


# TODO define: default configuation
DEFAULT_CONFIG = {
        REMOTE_API_PORT: 8008,
        LIGHTTOWER_PORT: 4242,
        DOCKER_BRIDGE: '172.17.42.1',
        DOCKER_API_VERSION: 'v1.14',
        DOCKER_PORT: 2375,
        MONGOS_PORT: 27017
}

_config = None

def _read_configuration(path):
    # TODO handle exceptions: file not found, yaml parse error -> return default config
    stream = open(path, 'r')
    return yaml.load(stream)

def get_configuration():
    global _config
    if not _config:
        try:
            path = os.environ['PHAROS_CONFIG']
            _config = _read_configuration(path)
        except KeyError:
            _config = DEFAULT_CONFIG
    return _config

def get_preference(field):
    if field not in CONFIG_FIELDS:
        # TODO implement: custom exception class ex) InvaildField
        raise Exception('%s is not vaild field name' % field)
    return get_configuration()[field]
