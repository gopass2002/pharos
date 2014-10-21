import argparse
import sys
import socket
import re
import json

import requests
import docker

from . import cmd
from pharos.common import (
    get_preference,
    print_divider,
    print_line
)

from pharos.common import (
    REMOTE_API_HOST,
    REMOTE_API_PORT,
    LIGHTTOWER_PORT,
    DOCKER_BRIDGE,
    DOCKER_PORT,
    MONGOS_PORT
)

COMMANDS = ['top', 'list', 'add', 'add', 'remove', 'run']

def _get_hostname(host):
    'if host is ip address, lookup and replace hostname'
    if host in ('localhost', '127.0.0.1'):
        host = socket.gethostname()
    match = re.match('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', host)
    if match:
        host = socket.gethostbyaddr(host)[0]
    return host


def get_base_url():
    return 'http://%s:%i' % (
        get_preference(REMOTE_API_HOST),
        get_preference(REMOTE_API_PORT))


top_parser = argparse.ArgumentParser()
top_parser.add_argument('host', help='target host to display')
@cmd(top_parser)
def top(args):
    'display <host> container\'s metrics'
    host = _get_hostname(args.host)
    from window import Top
    win = Top(host)
    win.start_display()


ls_parser = argparse.ArgumentParser()
@cmd(ls_parser)
def list(args):
    'list nodes'
    base_url = get_base_url()
    url = base_url + '/node'
    try:
        res = requests.get(url)
    except requests.exceptions.ConnectionError, e:
        print >> sys.stderr, url + ' is not available (Connection Refused)'
        print >> sys.stderr, 'are you start remote server?'
        exit(1)

    if res.status_code != 200:
        print 'empty'

    nodes = res.json()['nodes']
    print_divider('-')
    templ = '%-30s %-20s %-20s'
    header = ('ID', 'HOSTNAME', 'IP')
    print_line(templ % header)
    print_divider('-')
    for node in nodes:
        print_line(templ % (node['_id'], node['host'], socket.gethostbyname(node['host'])))
    print


add_parser = argparse.ArgumentParser()
add_parser.add_argument('host', help='to add hostname')
@cmd(add_parser)
def add(args):
    'add node'
    base_url = get_base_url()
    url = base_url + '/node'
    payload = {'host': args.host}
    headers = {'content-type': 'application/json'}

    try:
        res = requests.post(url, data=json.dumps(payload), headers=headers)
    except requests.exceptions.ConnectionError, e:
        print >> sys.stderr, url + ' is not available (Connection Refused)'
        print >> sys.stderr, 'are you start remote server?'
        exit(1)

    if res.status_code != 200:
        print res.json()['message']
    else:
        print res.json()['_id']

remove_parser = argparse.ArgumentParser()
remove_parser.add_argument('host', help='to remove hostname')
@cmd(remove_parser)
def remove(args):
    'remove node'
    base_url = get_base_url()
    url = base_url + '/node'
    payload = {'host': args.host}
    headers = {'content-type': 'application/json'}

    try:
        res = requests.delete(url, data=json.dumps(payload), headers=headers)
    except requests.exceptions.ConnectionError, e:
        print >> sys.stderr, url + ' is not available (Connection Refused)'
        print >> sys.stderr, 'are you start remote server?'
        exit(1)

    if res.status_code != 200:
        print res.json()

    print res.json()['_id']


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