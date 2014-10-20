# default modules
import argparse, os, socket
# third party modules
import requests
import docker
# pharos modules
from pharos.cli import cmd
from pharos._common import get_preference
from pharos._common import (REMOTE_API_HOST,
                            REMOTE_API_PORT,
                            LIGHTTOWER_PORT,
                            DOCKER_BRIDGE,
                            DOCKER_PORT,
                            MONGOS_PORT)

run_parser = argparse.ArgumentParser()
run_parser.add_argument('hostname', nargs='*', help='to run hosts')
run_parser.add_argument('-a', '--all', action='store_true', default=True, help='run all hosts')
run_parser.add_argument('-d', '--docker', action='store_true', help='run docker daemon')
@cmd(run_parser)
def run(args):
    'run lightkeeper daemons'
    remote_host = get_preference(REMOTE_API_HOST)
    remote_port = get_preference(REMOTE_API_PORT)
    lighttower_port = get_preference(LIGHTTOWER_PORT)
    docker_host = get_preference(DOCKER_BRIDGE)
    docker_port = get_preference(DOCKER_PORT)
    mongos_port = get_preference(MONGOS_PORT)

    url = 'http://%s:%i/node' % (remote_host, remote_port)
    
    res = requests.get(url)
    if res.status_code != 200:
        # TODO handle error
        print 'error'
    nodes = res.json()['nodes']
    name = 'pharos-lightkeeper'

    for node in nodes:
        c = docker.Client('tcp://%s:%i' % (node['host'], docker_port))
        print 'starting lightkeeper at %s' % node['host']
        try:
            c.inspect_container(name)
        except docker.errors.APIError:
            print 'create new container at %s' % node['host']
            container = c.create_container('pharos', 
                environment=[
                    'PHAROS_HOSTNAME=' + node['host'],
                    'LIGHTTOWER_PORT=' + str(lighttower_port),
                    'DOCKER_BRIDGE=' + docker_host,
                    'DOCKER_PORT=' + str(docker_port),
                    'MONGOS_PORT=' + str(mongos_port)],
                detach=True, 
                volumes={'/pharos/proc':'/proc'}, 
                name=name)
        c.start(name, binds={'/proc': '/pharos/proc'}, privileged=True)
        print 'successfully start lightkeeper'
