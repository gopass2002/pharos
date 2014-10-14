import argparse, os, socket
import pharos.cli
from pharos.cli import cmd

run_parser = argparse.ArgumentParser()
run_parser.add_argument('-d', '--docker', action='store_true', help='run docker daemon')
@cmd(run_parser)
def run(args):
    'run lightkeeper daemons'
    hostname = socket.gethostname()
    cmd = 'docker run -d --privileged=true -e DOCKER_HOST=%s -v /proc:/pharos/proc pharos' % (hostname)
    print cmd
    os.system(cmd)
