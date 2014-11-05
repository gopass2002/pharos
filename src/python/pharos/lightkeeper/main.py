# default modules
import os
import sys
import multiprocessing
import socket
import encodings.idna
import json
import argparse
import time

# exteranl modules
import docker
import pymongo
import numpy
import zmq
import zerorpc

# pharos modules
import pharos.config as Config
from node import Node

def monitor_events(conf, docker_client, mongos):
    events_col = mongos.pharos.events
    containers_col = mongos.pharos.containers
    container_metrics_col = mongos.pharos.container_metrics

    ctx = zmq.Context()
    event_sock = ctx.socket(zmq.PUSH)
    event_sock.connect('tcp://%s:%i' % (
            conf[Config.LIGHTTOWER_HOST], conf[Config.LIGHTTOWER_EVENT_COLLECT_PORT]
        )
    )

    # container event monitor process
    for e in docker_client.events():
        event = json.loads(e)
        status = event['status']
        container_id = event['id']
        
        # insert new container event
        events_col.insert(event)

        if status == 'die':
            # remove container metrics from container_metrics
            q = {'Id': container_id}
            print 'remove container metrics', container_metrics_col.remove({'Id': container_id})
            # update container laste status to container
            inspect = docker_client.inspect_container(container_id)
            print 'update container status', containers_col.update({'Id': inspect['Id']}, inspect, True)
        elif status == 'destroy':
            # remove container record from containers
            print 'remove container', containers_col.remove({'Id': container_id})
        print 'recv event', e
        event_sock.send(e)

def collect_metrics(conf, docker_client, mongos, is_container):
    node = Node(docker_client)
    hostname = conf['hostname']
    container_metrics_col = mongos.pharos.container_metrics
    containers_col = mongos.pharos.containers
    node_metrics_col = mongos.pharos.node_metrics
    interval = conf[Config.METRICS_COLLECT_INTERVAL]

    if is_container:
        os.chroot('/pharos')

    while True:
        containers = node.containers()
        node_doc = {'Host': hostname, 'Containers': []}
        if len(containers) == 0:
            # not exists running any container
            node_metrics = [0.0] * 10
            node_doc['Metrics'] = node_metrics
        else:
            # collect container metrics
            node_metrics = []
            for container in containers:
                try:
                    procs = container.processes()
                except docker.errors.APIError:
                    continue
                # inspect container status
                inspect = container.inspect()
                inspect['Host'] = hostname

                # update container status
                containers_col.update({'Id': inspect['Id']}, inspect, True)

                # aggregate container metrics
                metrics = container.metrics(procs)
                doc = {'Metrics': metrics}

                # add container status
                doc['Id'] = inspect['Id']
                doc['Image'] = inspect['Config']['Image']
                doc['Name'] = inspect['Name']
                doc['Host'] = hostname
                doc['Created'] = inspect['Created']
                doc['Started'] = inspect['State']['StartedAt']
                doc['Command'] = inspect['Config']['Cmd']
                node_doc['Containers'].append(doc)
                doc['Processes'] = procs

                # update container metrics to mongodb
                container_metrics_col.update({'Id': inspect['Id']}, doc, True)
                node_metrics.append(metrics)

            try:
                node_doc['Metrics'] = list(numpy.sum(node_metrics, axis=0))
            except TypeError:
                print node_metrics
                exit(1)
        # update node metrics to mongodb
        node_metrics_col.update({'Host': hostname}, node_doc, True)

        # sleep interval(default=1)
        time.sleep(interval)


def run_lightkeeper():
    is_container = os.path.exists('/.dockerinit')
    conf = {}
    if is_container:
        # in docker container, override ports and change root directory
        conf['hostname'] = os.environ['EXT_HOSTNAME']
        conf[Config.LIGHTTOWER_HOST] = os.environ['LIGHTTOWER_HOST']
        conf[Config.LIGHTTOWER_EVENT_COLLECT_PORT] = int(os.environ['LIGHTTOWER_EVENT_COLLECT_PORT'])
        conf[Config.LIGHTKEEPER_RPC_PORT] = int(os.environ['LIGHTKEEPER_RPC_PORT'])
        conf[Config.DOCKER_BRIDGE_IP] = os.environ['DOCKER_BRIDGE_IP']
        conf[Config.DOCKER_REMOTE_API_PORT] = int(os.environ['DOCKER_REMOTE_API_PORT'])
        #config[DOCKER_UNIX_SOCKET_PATH] = os.environ['DOCKER_UNIX_SOCKET_PATH']
        conf[Config.MONGOS_PORT] = int(os.environ['MONGOS_PORT'])
        conf[Config.METRICS_COLLECT_INTERVAL] = int(os.environ['METRICS_COLLECT_INTERVAL'])
    else:
        conf['hostname'] = socket.gethostname()
        conf[Config.LIGHTTOWER_HOST] = Config.get_preference(Config.LIGHTTOWER_HOST)
        conf[Config.LIGHTTOWER_EVENT_COLLECT_PORT] = Config.get_preference(Config.LIGHTTOWER_EVENT_COLLECT_PORT)
        conf[Config.DOCKER_BRIDGE_IP] = Config.get_preference(Config.DOCKER_BRIDGE_IP)
        conf[Config.DOCKER_REMOTE_API_PORT] = Config.get_preference(Config.DOCKER_REMOTE_API_PORT)
        #config[DOCKER_UNIX_SOCKET_PATH] = get_preference(DOCKER_UNIX_SOCKET_PATH)
        conf[Config.MONGOS_PORT] = Config.get_preference(Config.MONGOS_PORT)
        conf[Config.METRICS_COLLECT_INTERVAL] = Config.get_preference(Config.METRICS_COLLECT_INTERVAL)

    #docker_client = docker.Client('unix://%s' % config[DOCKER_UNIX_SOCKET_PATH])
    docker_client = docker.Client('tcp://%s:%i' % (conf[Config.DOCKER_BRIDGE_IP], conf[Config.DOCKER_REMOTE_API_PORT])) 
    mongos_client = pymongo.MongoClient(conf[Config.DOCKER_BRIDGE_IP], conf[Config.MONGOS_PORT])

    event_monitor = multiprocessing.Process(target=monitor_events, args=(conf, docker_client, mongos_client))
    event_monitor.daemon = True
    event_monitor.start()

    collector = multiprocessing.Process(target=collect_metrics, args=(conf, docker_client, mongos_client, is_container))
    collector.daemon = True
    collector.start()

    interval = conf[Config.METRICS_COLLECT_INTERVAL]
    
    while collector.is_alive() and event_monitor.is_alive():
        collector.join(interval)
        event_monitor.join(interval)

def main():
    run_lightkeeper()
