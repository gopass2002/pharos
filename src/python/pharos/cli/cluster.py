import argparse
import sys
import socket
import re
import json

import requests
import docker

from . import cmd

from pharos.common.util import print_divider, print_line
import pharos.config as Config
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
        Config.get_preference(Config.LIGHTTOWER_HOST),
        Config.get_preference(Config.LIGHTTOWER_REMOTE_API_PORT)
    )


top_node_parser = argparse.ArgumentParser()
top_node_parser.add_argument('host', help='target host to display')
top_node_parser.add_argument('-b', '--batch', action='store_true', help='display batch mode')
@cmd(top_node_parser)
def top_node(args):
    'display <host> node metrics'
    host = _get_hostname(args.host)
    from pharos.display.window import NodeTop
    win = NodeTop(host, console=args.batch)
    try:
        win.start_display()
    except requests.exceptions.ConnectionError:
        print 'Cannot connect pharos-remote-server'
        exit(1)

top_container_parser = argparse.ArgumentParser()
#top_container_parser.add_argument('host', help='target host to display container')
top_container_parser.add_argument('container_id', help='target container id to display')
top_container_parser.add_argument('-b', '--batch', action='store_true', help='display batch mode')
@cmd(top_container_parser)
def top_container(args):
    'display <container> metrics'
    from pharos.display.window import ContainerTop
    win = ContainerTop(args.container_id, console=args.batch)
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
    templ = '%-12s    %-40s   %-25s    %-10s  %-25s    %-15s'
    header = ('CONTAINER ID', 'IMAGE', 'COMMNAD', 'STATUS', 'NAMES', 'HOST')
    print_line(templ % header, highlight=True)
    for container in containers:
        cmd = '"%s %s"' % (container['Path'], ' '.join(container['Args']))
        status = 'running' if container['State']['Running'] else 'stopped'
        
        row = (
            container['Id'][:12], container['Config']['Image'], 
            cmd[:25], status, container['Name'][:25], container['Host']
        )
        print_line(templ % row)
            

nodes_parser = argparse.ArgumentParser()
@cmd(nodes_parser)
def nodes(args):
    'list nodes'
    base_url = get_base_url()
    url = base_url + '/nodes'
    
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
    url = base_url + '/nodes'
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
    url = base_url + '/nodes'
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
@cmd(run_parser)
def run(args):
    'run lightkeeper daemons'
    envs = {}
    envs['hostname'] = socket.gethostname()
    envs[Config.LIGHTTOWER_HOST] = Config.get_preference(Config.LIGHTTOWER_HOST)
    envs[Config.LIGHTTOWER_EVENT_COLLECT_PORT] = Config.get_preference(Config.LIGHTTOWER_EVENT_COLLECT_PORT)
    envs[Config.LIGHTKEEPER_RPC_PORT] = Config.get_preference(Config.LIGHTKEEPER_RPC_PORT)
    envs[Config.DOCKER_BRIDGE_IP] = Config.get_preference(Config.DOCKER_BRIDGE_IP)
    envs[Config.DOCKER_REMOTE_API_PORT] = Config.get_preference(Config.DOCKER_REMOTE_API_PORT)
    envs[Config.DOCKER_UNIX_SOCKET_PATH] = Config.get_preference(Config.DOCKER_UNIX_SOCKET_PATH)
    envs[Config.MONGOS_PORT] = Config.get_preference(Config.MONGOS_PORT)
    envs[Config.METRICS_COLLECT_INTERVAL] = Config.get_preference(Config.METRICS_COLLECT_INTERVAL)

    env_list = ['%s=%s' % (key.upper(), item) for (key, item) in envs.items()]

    remote_api_url = 'http://%s:%i/nodes' % (
            Config.get_preference(Config.LIGHTTOWER_HOST), 
            Config.get_preference(Config.LIGHTTOWER_REMOTE_API_PORT
        )
    )

    res = requests.get(remote_api_url)
    if res.status_code != 200:
        # TODO handle error
        print 'error'
    nodes = res.json()['nodes']
    name = 'pharos-lightkeeper'
    
    docker_port = Config.get_preference(Config.DOCKER_REMOTE_API_PORT)
    docker_socket = Config.get_preference(Config.DOCKER_UNIX_SOCKET_PATH)
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
                ports=[Config.get_preference(Config.LIGHTKEEPER_RPC_PORT)],
                name=name
            )

        c.start(name, binds={
                '/proc': '/pharos/proc',
                '/dev/null': '/pharos/dev/null'
            },
            network_mode='host', 
            privileged=True,
            port_bindings={
                Config.get_preference(Config.LIGHTKEEPER_RPC_PORT) : Config.get_preference(Config.LIGHTKEEPER_RPC_PORT)
            }
        )
        print 'successfully start lightkeeper'


