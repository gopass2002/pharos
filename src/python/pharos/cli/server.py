import argparse, re
import os, socket
import pharos.cli
import pymongo
from pharos.cli import cmd

start_parser = argparse.ArgumentParser()
start_parser.add_argument('port', nargs='?', type=int, default=8008, help='remote server port')
@cmd(start_parser)
def start(args):
    'start remote api server (default port: 8008)'
    from pharos import rest

    for name in rest.__views__:
        __import__('pharos.rest.%s' % name)
    rest.app.run(host='0.0.0.0', port=args.port, debug=True)
