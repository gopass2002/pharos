import docker
import zerorpc
import numpy

from pharos._docker import *

from pharos._common import (get_preference)
from pharos._common import (LIGHTTOWER_PORT, DOCKER_PORT)

class _Node(object):
    def __init__(self, host):
        self.host = host
    def containers(self):
        raise NotImplementedError
    def processes(self, container_id=None):
        raise NotImplementedError
    def metrics(self):
        raise NotImplementedError
    def container_metrics(self, container):
        raise NotImplementedError
    def process_metrics(self, container, pid):
        raise NotImplementedError

class NodeServer(_Node):
    def __init__(self, host):
        _Node.__init__(self, host)
        port = get_preference(DOCKER_PORT)
        self.client = docker.Client('tcp://%s:%i' % (host, port))
    
    def inspect_container(self, container_id):
        return self.client.inspect_container(container_id)

    def get_container(self, container_id):
        return Container(self.client, self.inspect_container(container_id))
    
    def containers(self):
        containers = [self.get_container(status['Id']) for status in self.client.containers()]
        return containers

    def processes(self, container_id=None):        
        if container_id:
            containers = [self.get_container(container_id)]
        else:
            containers = self.containers()
        procs = []
        for container in containers:
            procs.extend(container.processes())
        return procs

    def metrics(self, containers=None):
        if not containers:
            containers = self.containers()
        metrics = [container.metrics() for container in containers]
        if len(metrics) == 0:
            return [0.0] * 10
        return list(numpy.sum(metrics, axis=0))

    def container_metrics(self, container_id):
        container = self.get_container(container_id)
        return container.metrics() 

    def process_metrics(self, container_id, pid):
        container = self.get_container(container_id)
        return container.get_process(pid).metrics()


class Node(_Node):
    def __init__(self, host):
        _Node.__init__(self, host)
        self.host = host
        self.rpc = zerorpc.Client()
        self.rpc.connect('tcp://%s:%i' % (host, get_preference(LIGHTTOWER_PORT)))
        self.docker = docker.Client('tcp://%s:%i' % (self.host, get_preference(DOCKER_PORT)))
   
    def containers(self):
        return self.rpc.containers()

    def processes(self, container_id=None):
        return self.rpc.processes(container_id)

    def metrics(self):
        return self.rpc.metrics()

    def container_metrics(self, container):
        if type(container) == str:
            return self.rpc.container_metrics(container)
        return self.rpc.container_metrics(container)

    def process_metrics(self, container, pid):
        if type(container) == str:
            return self.rpc.process_metrics(container, pid)
        return self.rpc.process_metrics(container['Id'], pid)

    def attach(self, container):
        if type(container) == str:
            return self.docker.attach(container, stream=True)
        return self.docker.attach(container['Id'], stream=True)
