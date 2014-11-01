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
    LIGHTTOWER_HOST, LIGHTTOWER_EVENT_COLLECT_PORT, LIGHTTOWER_REMOTE_API_PORT,
    LIGHTKEEPER_RPC_PORT,
    DOCKER_BRIDGE_IP, DOCKER_UNIX_SOCKET_PATH, DOCKER_REMOTE_API_PORT,
    MONGOS_PORT,
    METRICS_COLLECT_INTERVAL,
)

#COMMANDS = ['top_conatiner', 'top_node', 'list', 'add', 'add', 'remove', 'run', 'containers']

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
        get_preference(LIGHTTOWER_HOST),
        get_preference(LIGHTTOWER_REMOTE_API_PORT)
    )


top_node_parser = argparse.ArgumentParser()
top_node_parser.add_argument('host', help='target host to display')
@cmd(top_node_parser)
def top_node(args):
    'display <host> node metrics'
    host = _get_hostname(args.host)
    from pharos.window import NodeTop
    win = NodeTop(host)
    try:
        win.start_display()
    except requests.exceptions.ConnectionError:
        print 'Cannot connect pharos-remote-server'
        exit(1)

top_container_parser = argparse.ArgumentParser()
top_container_parser.add_argument('host', help='target host to display container')
top_container_parser.add_argument('container_id', help='target container id to display')
@cmd(top_container_parser)
def top_container(args):
    'display <host> <container> metrics'
    host = _get_hostname(args.host)
    from pharos.window import ContainerTop
    win = ContainerTop(host, args.container_id)
    try:
        win.start_display()
    except requests.exceptions.ConnectionError:
        print 'Cannot connect pharos-remote-server'
        exit(1)


containers_parser = argparse.ArgumentParser()
containers_parser.add_argument('host', nargs='?', help='specify host to display')
containers_parser.add_argument('-a', '--all', action='store_true', default=False, help='show all containers')
containers_parser.add_argument('-q', '--quiet', action='store_true', default=False, help='only display numeric IDs')
@cmd(containers_parser)
def containers(args):
    'list containers'
    base_url = get_base_url()
    url = base_url + '/containers?'

    if args.host:
        url += 'host=' + args.host + '&'
    if args.all:
        url += 'all=true&'
    if args.quiet:
        url += 'quiet=true&'

    try:
        res = requests.get(url)
    except requests.exceptions.ConnectionError, e:
        print >> sys.stderr, url + ' is not available (Connection Refused)'
        print >> sys.stderr, 'are you start remote server?'
        exit(1)

    if res.status_code != 200:
        print 'Server Error[%i]: %s' % (res.json()['return_code'], res.json()['message'])
        exit(0)

    containers = res.json()['containers']
    templ = '%-12s    %-20s   %-25s    %-10s  %-25s    %-15s'
    header = ('CONTAINER ID', 'IMAGE', 'COMMNAD', 'STATUS', 'NAMES', 'HOST')
    print_line(templ % header, highlight=True)
    for container in containers:
        cmd = '"%s %s"' % (container['Path'], ' '.join(container['Args']))
        status = 'running' if container['State']['Running'] else 'stopped'
        
        row = (
            container['Id'][:12], container['Config']['Image'], 
            cmd[:25], status, container['Name'][:25], container['hostname']
        )
        print_line(templ % row)
            

nodes_parser = argparse.ArgumentParser()
@cmd(nodes_parser)
def nodes(args):
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
        print 'Server Error[%i]: %s' % (res.json()['return_code'], res.json()['message'])
        exit(0)
    
    nodes = res.json()['nodes']
    print_divider('-')
    templ = '%-30s %-20s %-10s %-10s %-12s %-20s'
    header = ('ID', 'HOSTNAME', 'DOCKER', 'STORAGE', 'CONTAINERS', 'IP')
    print_line(templ % header, highlight=True)
    print_divider('-')
    for node in nodes:
        containers = node['containers']
        docker_health = 'GONE' if containers < 0 else 'OK'
        storage_health = 'GONE' if not node['storage'] else 'OK'
        print_line(
            templ % (
                node['_id'], 
                node['host'], 
                docker_health,
                storage_health,
                containers,
                socket.gethostbyname(node['host'])
            )
        )
    print


add_node_parser = argparse.ArgumentParser()
add_node_parser.add_argument('host', help='to add hostname')
@cmd(add_node_parser)
def add_node(args):
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

remove_node_parser = argparse.ArgumentParser()
remove_node_parser.add_argument('host', help='to remove hostname')
@cmd(remove_node_parser)
def remove_node(args):
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


daemon_parser = argparse.ArgumentParser()
daemon_parser.add_argument('hostname', nargs='*', help='to run hosts')
daemon_parser.add_argument('-a', '--all', action='store_true', default=True, help='run all hosts')
daemon_parser.add_argument('-d', '--docker', action='store_true', help='run docker daemon')
@cmd(daemon_parser)
def daemon(args):
    'run lightkeeper daemons'
    envs = {}
    envs['hostname'] = socket.gethostname()
    envs[LIGHTTOWER_HOST] = get_preference(LIGHTTOWER_HOST)
    envs[LIGHTTOWER_EVENT_COLLECT_PORT] = get_preference(LIGHTTOWER_EVENT_COLLECT_PORT)
    envs[LIGHTKEEPER_RPC_PORT] = get_preference(LIGHTKEEPER_RPC_PORT)
    envs[DOCKER_BRIDGE_IP] = get_preference(DOCKER_BRIDGE_IP)
    envs[DOCKER_REMOTE_API_PORT] = get_preference(DOCKER_REMOTE_API_PORT)
    envs[DOCKER_UNIX_SOCKET_PATH] = get_preference(DOCKER_UNIX_SOCKET_PATH)
    envs[MONGOS_PORT] = get_preference(MONGOS_PORT)
    envs[METRICS_COLLECT_INTERVAL] = get_preference(METRICS_COLLECT_INTERVAL)

    env_list = ['%s=%s' % (key.upper(), item) for (key, item) in envs.items()]

    remote_api_url = 'http://%s:%i/node' % (
            get_preference(LIGHTTOWER_HOST), 
            get_preference(LIGHTTOWER_REMOTE_API_PORT
        )
    )

    res = requests.get(remote_api_url)
    if res.status_code != 200:
        # TODO handle error
        print 'error'
    nodes = res.json()['nodes']
    name = 'pharos-lightkeeper'
    
    docker_port = get_preference(DOCKER_REMOTE_API_PORT)
    docker_socket = get_preference(DOCKER_UNIX_SOCKET_PATH)
    for node in nodes:
        c = docker.Client('tcp://%s:%i' % (node['host'], docker_port))
        print 'starting lightkeeper at %s' % node['host']
        env_pairs = ['EXT_HOSTNAME=' + node['host'], 'HOME=/pharos']
        env_pairs.extend(env_list)
        try:
            c.inspect_container(name)
        except docker.errors.APIError:
            print 'create new container at %s' % node['host']
            container = c.create_container(
                'gopass2002/pharos',
                environment=env_pairs,
                detach=True,
                volumes={
                    '/pharos/proc': '/proc',
                    '/pharos/dev/null': '/dev/null'
                },
                ports=[get_preference(LIGHTKEEPER_RPC_PORT)],
                name=name
            )

        c.start(name, binds={
                '/proc': '/pharos/proc',
                '/dev/null': '/pharos/dev/null'
            },
            network_mode='host', 
            privileged=True,
            port_bindings={
                get_preference(LIGHTKEEPER_RPC_PORT) : get_preference(LIGHTKEEPER_RPC_PORT)
            }
        )
        print 'successfully start lightkeeper'


