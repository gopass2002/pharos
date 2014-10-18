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
        cmd = 'docker run -d --net=host --privileged=true --name=pharos-lightkeeper -v /proc:/pharos/proc pharos'
        print cmd
        os.system(cmd)
            
