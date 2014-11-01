import requests

import zmq

from node import Node
# TODO implement: another database or filesystem likes as db
from common import (
    get_configuration,
    get_preference
)
from common import (
    LIGHTTOWER_HOST,
    LIGHTTOWER_REMOTE_API_PORT,
    LIGHTTOWER_EVENT_BROADCAST_PORT
)

__all__ = ['cli']

_client = None

def client():
    global _client

    if not _client:
        config = get_configuration()  
        _client = PharosClient(config)
    return _client

class PharosClient(object):
    def __init__(self, config):
        self.config = config

    def get_configuration(self):
        return self.config

    def containers(self, nodes=None):
        if not nodes:
            nodes = self.nodes()
        containers = []
        for node in nodes():
            containers += node.containers()
        
        return containers

    def hosts(self):
        url = 'http://%s:%i/node' % (
            get_preference(LIGHTTOWER_HOST),
            get_preference(LIGHTTOWER_REMOTE_API_PORT)    
        )
        try:
            res = requests.get(url)
        except requests.exceptions.ConnectionError, e:
            print >> sys.stderr, url + ' is not available (Connection Refused)'
            print >> sys.stderr, 'are you start remote server?'
        if res.status_code != 200:
            print 'Server Error[%i]: %s' % (res.json()['return_code'], res.json()['message'])

        return res.json()['nodes'] 

    def nodes(self):
        return [Node(host['host']) for host in self.hosts()]
    
    def get_node(self, host):
        return Node(host)

class EventListener(object):
    def __init__(self, handler):
        self.host = get_preference(LIGHTTOWER_HOST)
        self.port = get_preference(LIGHTTOWER_EVENT_BROADCAST_PORT)
        self.ctx = zmq.Context()
        self.sock = self.ctx.socket(zmq.SUB)
        self.handler = handler

    def subscribe(self, host='', container=''):
        self.sock.setsockopt_string(zmq.SUBSCRIBE, u'%s%s' % (host, container))

    def listen(self, blocking=False):
        self.sock.connect('tcp://%s:%i' % (self.host, self.port))

        if blocking:
            print 'blocking'
            self._listen()
        else:
            print 'non-blockking'
            import threading
            listener = threading.Thread(target=self._listen())
            listener.setDaemon(True)
            listener.start()

    def _listen(self):
        while True:
            msg = self.sock.recv()
            self.handler(msg)


