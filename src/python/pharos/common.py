import os
import yaml
import fcntl, termios, struct

# config headers
HEADER_PHAROS = 'pharos'
HEADER_PHAROS_LIGHTTOWER = 'lighttower'
HEADER_PHAROS_LIGHTKEEPER = 'lightkeeper'
HEADER_DOCKER = 'docker'
HEADER_MONGODB = 'mongodb'

# pharos
METRICS_COLLECT_INTERVAL = 'metrics_collect_interval'
STORAGE_TYPE = 'storage_type'

# light_tower
LIGHTTOWER_HOST = 'lighttower_host'
LIGHTTOWER_EVENT_BROADCAST_PORT = 'lgihttower_event_boradcast_port'
LIGHTTOWER_EVENT_COLLECT_PORT = 'lighttower_event_collect_port'
LIGHTTOWER_REMOTE_API_PORT = 'lighttower_remote_api_port'

# light_port
LIGHTKEEPER_RPC_PORT = 'lightkeeper_rpc_port'

# docker
DOCKER_BRIDGE_IP = 'docker_bridge_ip'
DOCKER_UNIX_SOCKET_PATH = 'docker_unix_socket_path'
DOCKER_REMOTE_API_PORT = 'docker_remote_api_port'
DOCKER_REMOTE_API_VERSION = 'docker_api_version'

# mongodb
MONGOS_PORT = 'mongos_port'

CONFIG_FIELDS = (
    METRICS_COLLECT_INTERVAL, STORAGE_TYPE,
    LIGHTTOWER_HOST, LIGHTTOWER_EVENT_BROADCAST_PORT, LIGHTTOWER_EVENT_COLLECT_PORT, LIGHTTOWER_REMOTE_API_PORT,
    LIGHTKEEPER_RPC_PORT,
    DOCKER_BRIDGE_IP, DOCKER_UNIX_SOCKET_PATH, DOCKER_REMOTE_API_PORT, DOCKER_REMOTE_API_VERSION,
    MONGOS_PORT,
)

# TODO define: default configuation
DEFAULT_CONFIG = {
    HEADER_PHAROS: {
        METRICS_COLLECT_INTERVAL: 1,
        STORAGE_TYPE: 'mongodb',

        HEADER_PHAROS_LIGHTTOWER: {
            LIGHTTOWER_HOST: 'localhost',
            LIGHTTOWER_EVENT_BROADCAST_PORT: 4242,
            LIGHTTOWER_EVENT_COLLECT_PORT: 4343,
            LIGHTTOWER_REMOTE_API_PORT: 4444
        },
        HEADER_PHAROS_LIGHTKEEPER: {
            LIGHTKEEPER_RPC_PORT: 5555
        }
    },
    HEADER_DOCKER: {
        DOCKER_BRIDGE_IP: '172.17.42.1',
        DOCKER_UNIX_SOCKET_PATH: '/var/run/docker.sock',
        DOCKER_REMOTE_API_PORT: 2375,
        DOCKER_REMOTE_API_VERSION: 'v1.14'
    },
    HEADER_MONGODB: {
        MONGOS_PORT: 27017
    }
}

DEFAULT_CONFIG_PATH = os.environ['HOME'] + '/etc/pharos.yml'

config = None

def read_configuration(path=DEFAULT_CONFIG_PATH):
    try:
        stream = open(path, 'r')
    except IOError, e:
        return DEFAULT_CONFIG
    return yaml.load(stream)

def get_configuration():
    global config
    if config:
        return config

    _config = DEFAULT_CONFIG
    try:
        path = os.environ['PHAROS_CONFIG']
        _config.update(read_configuration(path))
    except KeyError:
        pass
    config = _config

    return config

def _get_preference(field, config):
    if field in config:
        return config[field]

    configs = []
    for item in config.values():
        if type(item) == dict:
            value = _get_preference(field, item)
            if value:
                return value

    return None

def get_preference(field):
    if field not in CONFIG_FIELDS:
        raise Exception('%s is invaild field name' % field)
    return _get_preference(field, get_configuration())

def terminal_size():
    h, w, hp, wp = struct.unpack('HHHH',
        fcntl.ioctl(0, termios.TIOCGWINSZ,
        struct.pack('HHHH', 0, 0, 0, 0)))
    return w, h

def print_divider(char='-', highlight=False):
    max_w, max_h = terminal_size()
    print_line(char * max_w, highlight=highlight)

def print_line(line, highlight=False):
     max_w, max_h = terminal_size()
     if len(line) > max_w:  
        if highlight:  
            print '\033[1m' + line[:max_w] + '\033[0m'
        else:
            print line[:max_w]
            
     else:  
        if highlight:
            print '\033[1m' + line + '\033[0m'
        else:
            print line
