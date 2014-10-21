import docker
import zerorpc
import numpy
import psutil

from common import (get_preference)
from common import (LIGHTTOWER_PORT, DOCKER_PORT)


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


class Container(dict):
    def __init__(self, client, status):
        dict.__init__(self)
        self.client = client
        self.update(status)

    def pids(self):
        return [int(proc[1]) for proc in self.client.top(self['Id'])['Processes']]

    def get_process(self, pid):
        return Process(pid)

    def processes(self):
        procs = []
        for pid in self.pids():
            try:
                p = Process(pid)
            except psutil.NoSuchProcess:
                continue
            procs.append(p)
        return procs

    def metrics(self, processes=None):
        if not processes:
            processes = self.processes()
        metrics = [process.metrics() for process in processes]
        if len(metrics) == 0:
            return [0.0] * 10
        return list(numpy.sum(metrics, axis=0))


class Process(dict):
    def __init__(self, pid):
        self.pid = pid
        self.proc = psutil.Process(pid)
        self.update(self.proc.as_dict())

    def metrics(self):
        '''retrun (cpu_percent, cpu_times_user, cpu_times_system,
                    memomy_percent, memory_rss, memory_vms,
                    io_counter_read, io_counter_write,
                    network_recv_bytes, network_read_bytes'''
        try:
            proc = self.proc
            cpu_percent = proc.cpu_percent()
            cpu_times = proc.cpu_times()
            mem_percent = proc.memory_percent()
            mem_info = proc.memory_info()
            io_counters = proc.io_counters()
            net_counters = self._net_io_counters()
        except psutil.AccessDenied:
            print 'Could not access /proc/%s are you root?' % self.pid
            exit(1)

        metric = [
            cpu_percent, cpu_times[0], cpu_times[1],
            mem_percent, mem_info[0], mem_info[1],
            io_counters[2], io_counters[3],
            net_counters[0], net_counters[1]
        ]
        return metric

    def _net_io_counters(self):
        f = open("/proc/" + str(self.pid) + "/net/dev", "rt")
        try:
            lines = f.readlines()
        finally:
            f.close()

        bytes_recv_sum = 0
        bytes_sent_sum = 0
        for line in lines[2:]:
            colon = line.rfind(':')
            assert colon > 0, repr(line)
            name = line[:colon].strip()
            fields = line[colon + 1:].strip().split()
            bytes_recv_sum += int(fields[0])
            bytes_sent_sum += int(fields[8])
        return (bytes_recv_sum, bytes_sent_sum)

    def __str__(self):
        return str({'pid': self.pid, 'status': self.status, 'name': self.name, 'cmdline': self.cmdline})

    def __repr__(self):
        return '<%s(pid=%i) at %s' % (self.__class__.__name__, self.pid, id(self))
