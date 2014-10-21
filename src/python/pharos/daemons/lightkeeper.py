# default modules
import os, sys, multiprocessing
import socket
import encodings.idna, json
import argparse
import time

# exteranl modules
import docker
import pymongo
import numpy

try:
    from pharos import *
    from pharos._node import NodeServer
except ImportError:
    # in host, add python paths
    sys.path.append('../src/python')
    from pharos import *
    from pharos._node import NodeServer

IGNORE_EVENTS = ('create', 'destroy', 'export', 'kill', 'stop')
START_EVENTS = ('start', 'restart', 'unpause')
END_EVENTS = ('die', 'pause')

def monitor_events(mongos, hostname, host, port):
    # container event monitor process
    c = docker.Client('tcp://%s:%i' % (host, port))
    event_col = mongos.pharos.events
    con_col = mongos.pharos.container_metrics
    try:
        for e in c.events():
            event = json.loads(e)
            # status is 10 status
            # (create, destroy, die, export, kill, pause, restart, start, stop, unpause)
            status = event['status']
            q = {'id': event['id']}

            # TODO hadle result ex-> when result['n'] < 1 or result['ok'] != 1
            result = event_col.update(q, event, True)

            # sync metrics -> remove existing records
            if status in END_EVENTS:
                # TODO hadle result ex-> when result['n'] < 1 or result['ok'] != 1
                result = con_col.remove({'Id': event['id']})

    except KeyboardInterrupt:
        pass

def run_lightkeeper(args):
    hostname = socket.gethostname()
    host = hostname
    docker_port = args.docker_port
    mongos_port = args.mongo_port

    if os.path.exists('/.dockerinit'):
        # in docker container, override ports and change root directory
        hostname = os.environ['PHAROS_HOSTNAME']
        host = os.environ['DOCKER_BRIDGE']
        docker_port = int(os.environ['DOCKER_PORT'])
        mongos_port = int(os.environ['MONGOS_PORT'])
        os.chroot('/pharos')

    node = NodeServer(host)
    mongos = pymongo.MongoClient(host, mongos_port)
    container_col = mongos.pharos.container_metrics
    node_col = mongos.pharos.node_metrics

    p = multiprocessing.Process(target=monitor_events, args=(mongos, hostname, host, docker_port))
    p.start()

    q = {'hostname': hostname}
    try:
        while True:
            containers = node.containers()
            node_doc = {'hostname': hostname, 'containers': []}
            if len(containers) == 0:
                # it is not running any container
                node_metrics = [0.0] * 10
                node_doc['metrics'] = node_metrics
            else:
                node_metrics = []
                for container in containers:
                    try:
                        procs = container.processes()
                    except docker.errors.APIError:
                        continue

                    # aggregate container metrics
                    metrics = container.metrics(procs)
                    doc = {'metrics': metrics}

                    # add container status
                    doc.update(container)
                    node_doc['containers'].append(doc)
                    doc['processes'] = procs

                    # insert container metrics to mongodb
                    container_col.update({'Id': container['Id']},doc, True)
                    node_metrics.append(metrics)

                node_doc['metrics'] = list(numpy.sum(node_metrics, axis=0))
            node_col.update({'hostname': hostname}, node_doc, True)

            # sleep interval(default=1)
            time.sleep(args.interval)
    except KeyboardInterrupt:
        if p.is_alive():
            p.terminate()
        print 'good bye'

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--interval', type=int, default=1, help='collect metrics interval')
    parser.add_argument('--mongo_port', type=int, default=27017, help='mongos port')
    parser.add_argument('--docker_port', type=int, default=2375, help='docker port')
    args = parser.parse_args()

    run_lightkeeper(args)