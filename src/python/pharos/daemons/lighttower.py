import os, socket
import argparse

import zerorpc
from pharos._common import get_preference
from pharos._common import LIGHTTOWER_PORT
from pharos._node import NodeServer

def light_up(args):
    hostname = socket.gethostname()
    host = hostname
    port = args.port
    if os.path.exists('/.dockerinit'):
        port = int(os.environ['LIGHTTOWER_PORT'])

    tower = zerorpc.Server(NodeServer(hostname))
    tower.bind('tcp://0.0.0.0:%i' % port)
    tower.run()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=get_preference(LIGHTTOWER_PORT), help='lighttower bind port')
    args = parser.parse_args()
    light_up(args)