import argparse
import os, subprocess

from pharos.cli import cmd
from pharos._common import (get_preference)
from pharos._common import (REMOTE_API_PORT)

start_parser = argparse.ArgumentParser()
start_parser.add_argument('-f', '--foreground', action='store_true', default=False, help='start foreground mode')
@cmd(start_parser)
def start(args):
    'start remote api server (default port: 8008)'
    
    #port = get_preference(REMOTE_API_PORT)
    #cmd = 'pharos-remote-server'
    #if args.foreground:
    #    pid = os.spawnl(os.P_WAIT, cmd, '--port=' + str(port))
    #    print pid
    #else:
    #    pass
        #cmd += '1> /dev/null 2> /dev/null &'
        #os.system(cmd)
        #pid = os.spawnl(os.P_NOWAITO, cmd)
    #print 'successfully start pharos remote api server with pid=%d' % pid
