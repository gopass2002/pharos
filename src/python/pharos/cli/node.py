import argparse, re, json
import os, socket
import pharos.cli
from pharos.cli import print_line, print_divider
import pymongo
import requests
from pharos.cli import cmd
from ._common import get_remote_server_addr

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
    url = get_remote_server_addr() + '/node'
    try:
        res = requests.get(url)
    except requests.exceptions.ConnectionError, e:
        print >> sys.stderr, base_url + ' is not available (Connection Refused)'
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
    
    url = get_remote_server_addr() + '/node'
    payload = {'host': args.host}
    headers = {'content-type': 'application/json'}
    
    try:
        res = requests.post(url, data=json.dumps(payload), headers=headers)
    except requests.exceptions.ConnectionError, e:
        print >> sys.stderr, base_url + ' is not available (Connection Refused)'
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
    
    url = get_remote_server_addr() + '/node'
    payload = {'host': args.host}
    headers = {'content-type': 'application/json'}

    try:
        res = requests.delete(url, data=json.dumps(payload), headers=headers)
    except requests.exceptions.ConnectionError, e:
        print >> sys.stderr, base_url + ' is not available (Connection Refused)'
        print >> sys.stderr, 'are you start remote server?'
        exit(1)

    if res.status_code != 200:
        print res.json()

    print res.json()['_id']
