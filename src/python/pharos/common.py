import os
import yaml
import fcntl, termios, struct

# configuration field headers
REMOTE_API_HOST = 'remote_api_host',
REMOTE_API_PORT = 'remote_api_port',
LIGHTTOWER_PORT = 'lighttower_port',
DOCKER_BRIDGE = 'docker_bridge'
DOCKER_PORT = 'docker_port'
DOCKER_API_VERSION = 'docker_api_version'
MONGOS_PORT = 'mongo_port'
CONFIG_FIELDS = (
    REMOTE_API_HOST, REMOTE_API_PORT, LIGHTTOWER_PORT,
    DOCKER_BRIDGE, DOCKER_PORT, DOCKER_API_VERSION, MONGOS_PORT,)


# TODO define: default configuation
DEFAULT_CONFIG = {
        REMOTE_API_HOST: 'localhost',
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
