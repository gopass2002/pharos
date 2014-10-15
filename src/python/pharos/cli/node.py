import argparse, re
import os, socket
import pharos.cli
from pharos.cli import print_line, print_divider
import pymongo
import requests
from pharos.cli import cmd

def _get_hostname(host):
    'if host is ip address, lookup and replace hostname'
    if host in ('localhost', '127.0.0.1'):
        host = socket.gethostname()
    match = re.match('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', host)
    if match:
        host = socket.gethostbyaddr(host)[0]
    return host 

top_parser = argparse.ArgumentParser()
top_parser.add_argument('host', help='target host to display')
@cmd(top_parser)
def top(args):
    'display <host> container\'s metrics'
    host = _get_hostname(args.host)
    from pharos.cli.display import Top
    top = Top(host)
    top.start_display()

ls_parser = argparse.ArgumentParser()
@cmd(ls_parser)
def ls(args):
    'list nodes'
    res = requests.get(url='http://localhost:8008/node')
    if res.status_code != 200:
        print 'empty'
    
    nodes = res.json()['nodes']
    print_divider('-')
    templ = '%-30s %-20s %-15s %-15s'
    header = ('ID', 'HOST', 'DOCKER_PORT', 'MONGOS_PORT')
    print_line(templ % header)
    print_divider('-') 
    for node in nodes:
        print_line(templ % (node['_id'], node['host'], node['docker_port'], node['mongos_port']))
    print


add_parser = argparse.ArgumentParser()
add_parser.add_argument('host', help='to add hostname')
@cmd(add_parser)
def add(args):
    'add node'
    # TODO implement: reference config file 
    pass
