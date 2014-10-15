import argparse, os, socket
import pharos.cli
from pharos.cli import cmd

run_parser = argparse.ArgumentParser()
run_parser.add_argument('-d', '--docker', action='store_true', help='run docker daemon')
@cmd(run_parser)
def run(args):
    'run lightkeeper daemons'
    hostname = socket.gethostname()
    import docker
    c = docker.Client('tcp://localhost:2375')
    try:
        c.inspect_container('pharos-lightkeeper')
        c.restart('pharos-lightkeeper')
    except docker.errors.APIError:
        cmd = 'docker run -d --privileged=true --name=pharos-lightkeeper -e DOCKER_HOST=%s -v /proc:/pharos/proc pharos' % (
            hostname)
        print cmd
        os.system(cmd)
            
