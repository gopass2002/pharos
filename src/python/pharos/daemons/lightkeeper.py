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
from pharos.common import (get_preference)
from pharos.common import (
    LIGHTTOWER_HOST, LIGHTTOWER_EVENT_COLLECT_PORT,
    LIGHTKEEPER_RPC_PORT,
    DOCKER_BRIDGE_IP, DOCKER_UNIX_SOCKET_PATH, DOCKER_REMOTE_API_PORT,
    MONGOS_PORT,
    METRICS_COLLECT_INTERVAL,
)

from pharos.node import NodeServer

def monitor_events(config, docker_client):
    ctx = zmq.Context()
    event_sock = ctx.socket(zmq.PUSH)
    event_sock.connect('tcp://%s:%i' % (
            config[LIGHTTOWER_HOST], config[LIGHTTOWER_EVENT_COLLECT_PORT]
        )
    )

    # container event monitor process
    for e in docker_client.events():
        print 'event:', e
        event_sock.send(e)

def start_rpc_service(config, docker_client):
    tower = zerorpc.Server(NodeServer(docker_client), heartbeat=5)
    tower.bind('tcp://*:%i' % config[LIGHTKEEPER_RPC_PORT])
    tower.run()

def collect_metrics(config, docker_client, mongos, is_container):
    node = NodeServer(docker_client)
    hostname = config['hostname']
    container_col = mongos.pharos.container_metrics
    node_col = mongos.pharos.node_metrics
    interval = config[METRICS_COLLECT_INTERVAL]

    if is_container:
        os.chroot('/pharos')

    while True:
        containers = node.containers()
        node_doc = {'hostname': hostname, 'containers': []}
        if len(containers) == 0:
            # not exists running any container
            node_metrics = [0.0] * 10
            node_doc['metrics'] = node_metrics
        else:
            # collect container metrics
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

                # update container metrics to mongodb
                container_col.update({'Id': container['Id']},doc, True)
                node_metrics.append(metrics)

            try:
                node_doc['metrics'] = list(numpy.sum(node_metrics, axis=0))
            except TypeError:
                print node_metrics
                exit(1)
        # update node metrics to mongodb
        node_col.update({'hostname': hostname}, node_doc, True)

        # sleep interval(default=1)
        time.sleep(interval)


def run_lightkeeper():
    is_container = os.path.exists('/.dockerinit')
    config = {}
    if is_container:
        # in docker container, override ports and change root directory
        config['hostname'] = os.environ['EXT_HOSTNAME']
        config[LIGHTTOWER_HOST] = os.environ['LIGHTTOWER_HOST']
        config[LIGHTTOWER_EVENT_COLLECT_PORT] = int(os.environ['LIGHTTOWER_EVENT_COLLECT_PORT'])
        config[LIGHTKEEPER_RPC_PORT] = int(os.environ['LIGHTKEEPER_RPC_PORT'])
        config[DOCKER_BRIDGE_IP] = os.environ['DOCKER_BRIDGE_IP']
        config[DOCKER_REMOTE_API_PORT] = int(os.environ['DOCKER_REMOTE_API_PORT'])
        #config[DOCKER_UNIX_SOCKET_PATH] = os.environ['DOCKER_UNIX_SOCKET_PATH']
        config[MONGOS_PORT] = int(os.environ['MONGOS_PORT'])
        config[METRICS_COLLECT_INTERVAL] = int(os.environ['METRICS_COLLECT_INTERVAL'])
    else:
        config['hostname'] = socket.gethostname()
        config[LIGHTTOWER_HOST] = get_preference(LIGHTTOWER_HOST)
        config[LIGHTTOWER_EVENT_COLLECT_PORT] = get_preference(LIGHTTOWER_EVENT_COLLECT_PORT)
        config[LIGHTKEEPER_RPC_PORT] = get_preference(LIGHTKEEPER_RPC_PORT)
        config[DOCKER_BRIDGE_IP] = get_preference(DOCKER_BRIDGE_IP)
        config[DOCKER_REMOTE_API_PORT] = get_preference(DOCKER_REMOTE_API_PORT)
        #config[DOCKER_UNIX_SOCKET_PATH] = get_preference(DOCKER_UNIX_SOCKET_PATH)
        config[MONGOS_PORT] = get_preference(MONGOS_PORT)
        config[METRICS_COLLECT_INTERVAL] = get_preference(METRICS_COLLECT_INTERVAL)

    #docker_client = docker.Client('unix://%s' % config[DOCKER_UNIX_SOCKET_PATH])
    docker_client = docker.Client('tcp://%s:%i' % (config[DOCKER_BRIDGE_IP], config[DOCKER_REMOTE_API_PORT])) 
    mongos_client = pymongo.MongoClient(config[DOCKER_BRIDGE_IP], config[MONGOS_PORT])

    event_monitor = multiprocessing.Process(target=monitor_events, args=(config, docker_client))
    event_monitor.daemon = True
    event_monitor.start()

    rpc_server = multiprocessing.Process(target=start_rpc_service, args=(config, docker_client))
    rpc_server.daemon = True
    rpc_server.start()
    
    collector = multiprocessing.Process(target=collect_metrics, args=(config, docker_client, mongos_client, is_container))
    collector.daemon = True
    collector.start()

    interval = config[METRICS_COLLECT_INTERVAL]
    
    while collector.is_alive() and event_monitor.is_alive() and rpc_server.is_alive():
        collector.join(interval)
        event_monitor.join(interval)
        rpc_server.join(interval)

def main():
    run_lightkeeper()
