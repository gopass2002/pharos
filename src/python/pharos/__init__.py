import requests

import zmq

# TODO implement: another database or filesystem likes as db
'''
from .common import (
    get_configuration,
    get_preference
)
from common import (
    LIGHTTOWER_HOST,
    LIGHTTOWER_REMOTE_API_PORT,
    LIGHTTOWER_EVENT_BROADCAST_PORT
)

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

'''
