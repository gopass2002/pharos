# default modules
import os
import socket
import multiprocessing
import json

# 3rd party modules
import zmq
import zerorpc
import pymongo

# pharos modules
import pharos.config as conf

# events
IGNORE_EVENTS = ('create', 'destroy', 'export', 'kill', 'stop')
START_EVENTS = ('start', 'restart', 'unpause')
END_EVENTS = ('die', 'pause')

def run_rest_server(config):
    import pharos.lighttower as rest
    for name in rest.__VIEWS__:
        __import__('pharos.lighttower.%s' % name)
    try:
        rest.app.run(host='0.0.0.0', port=config[conf.LIGHTTOWER_REMOTE_API_PORT])
    except socket.error, (e, m):
        print 'could not open socket:', m

def monitor_events(config):
    mongos = pymongo.MongoClient('localhost', config[conf.MONGOS_PORT])
    container_metric_collection = mongos.pharos.container_metrics

    ctx = zmq.Context()
    monitor_sock = ctx.socket(zmq.PULL)
    monitor_sock.bind('tcp://*:%i' % config[conf.LIGHTTOWER_EVENT_COLLECT_PORT])
    
    broadcast_sock = ctx.socket(zmq.PUB)
    broadcast_sock.bind('tcp://*:%i' % config[conf.LIGHTTOWER_EVENT_BROADCAST_PORT])
    try:
        print 'start monitor'
        while True:
            msg = monitor_sock.recv()
            event = json.loads(msg)
            if event['status'] in END_EVENTS:
                print 'remove', container_metric_collection.remove({'Id': event['id']})
            print event
            broadcast_sock.send(msg)
    except BaseException, e:
        # TODO handle Exceptions
        print e
    finally:
        monitor_sock.close()
        broadcast_sock.close()

def run_lighttower():
    pid = os.getpid()

    config = {}
    config['hostname'] = socket.gethostname()
    config[conf.LIGHTTOWER_EVENT_BROADCAST_PORT] = conf.get_preference(conf.LIGHTTOWER_EVENT_BROADCAST_PORT)
    config[conf.LIGHTTOWER_EVENT_COLLECT_PORT] = conf.get_preference(conf.LIGHTTOWER_EVENT_COLLECT_PORT)
    config[conf.LIGHTTOWER_REMOTE_API_PORT] = conf.get_preference(conf.LIGHTTOWER_REMOTE_API_PORT)
    config[conf.MONGOS_PORT] = conf.get_preference(conf.MONGOS_PORT)
    
    rest_server = multiprocessing.Process(name='rest_api_server', target=run_rest_server, args=(config,))
    rest_server.daemon = True
    rest_server.start()

    event_monitor = multiprocessing.Process(name='event_monitor', target=monitor_events, args=(config,))
    event_monitor.daemon = True
    event_monitor.start()

    interval = conf.get_preference(conf.METRICS_COLLECT_INTERVAL)

    while rest_server.is_alive() and event_monitor.is_alive():
        rest_server.join(interval)
        event_monitor.join(interval)

def main():
    try:
        run_lighttower()
    except KeyboardInterrupt:
        print 'good bye'
