import docker
import zerorpc
import numpy
import psutil
import requests

import pharos.config as Config
from pharos.common.data import Metrics

class Node(object):
    def __init__(self, docker_client):
        self.docker = docker_client
        self.current_cts = {}

    def _add(self, container_id):
        container = Container(container_id, self.docker)
        self.current_cts[container_id] = container
        return container

    def _remove(self, container_id):
        self.current_cts.pop(container_id, None) 

    def get_container(self, container_id):
        if container_id not in self.current_cts:
            return self._add(container_id)
        return self.current_cts[container_id]

    def get_cids(self):
        return [container['Id'] for container in self.docker.containers(quiet=True)]

    def container_iter(self):
        a = set(self.get_cids())
        b = set(self.current_cts.keys())
        new_cids = a - b
        gone_cids = b - a

        for cid in gone_cids:
            self._remove(cid)
        for cid, container in sorted(list(self.current_cts.items()) + list(dict.fromkeys(new_cids).items())):
            if container is None: # new container
                yield self._add(cid)
            else: 
                yield container
    
    def containers(self):
        return list(self.container_iter())

    def processes(self, container_id=None): 
        if container_id:
            return self.get_container(container_id).processes()
        else:
            procs = []
            for container in self.container_iter():
                procs.extend(container.processes())
            return procs

    def metrics(self):
        metrics = [container.metrics() for container in self.container_iter()]
        if len(metrics) == 0:
            return [0.0] * 10
        return Metrics(*numpy.sum(metrics, axis=0))

    def container_metrics(self, container_id):
        container = self.get_container(container_id)
        return container.metrics() 

    def process_metrics(self, container_id, pid):
        container = self.get_container(container_id)
        return container.get_process(pid).metrics()

class Container(object):
    def __init__(self, container_id, docker):
        self.container_id = container_id
        self.docker = docker
        self.current_procs = {}
        status = self.inspect()
        self.pid = status['State']['Pid']
        self.main_proc = psutil.Process(self.pid)

    def _add(self, pid):
        process = Process(pid)
        self.current_procs[pid] = process
        return process

    def _remove(self, pid):
        self.current_procs.pop(pid, None)

    def get_id(self):
        return self.container_id

    def inspect(self):
        return self.docker.inspect_container(self.container_id)

    def pids(self):
        return [int(proc[1]) for proc in self.docker.top(self.container_id)['Processes']]

    def get_process(self, pid):
        if pid not in self.current_procs:
            return self._add(pid)
        return self.current_procs[pid]

    def process_iter(self):
        a = set(self.pids())
        b = set(self.current_procs.keys())
        new_pids = a - b
        gone_pids = b - a

        for pid in gone_pids:
            self._remove(pid)
        for pid, proc in sorted(list(self.current_procs.items()) + 
                list(dict.fromkeys(new_pids).items())):
            if proc is None:
                try:
                    yield self._add(pid)
                except psutil.NoSuchProcess:
                    continue
            else:
                yield proc

    def processes(self):
        return list(self.process_iter())

    def metrics(self, processes=None):
        metrics = [proc.metrics() for proc in self.process_iter()]
        io_counters = self.main_proc.io_counters()
        net_io_counters = self.net_io_counters()
        io_metrics = Metrics(
            cpu_percent=0.0,
            cpu_times_user=0.0,
            cpu_times_system=0.0,
            memory_percent=0.0,
            memory_rss=0.0,
            memory_vms=0.0,
            io_counter_read=io_counters[2],
            io_counter_write=io_counters[3],
            network_recv_bytes=net_io_counters[0],
            network_send_bytes=net_io_counters[1],
        )
        metrics.append(io_metrics) 
        
        return Metrics(*(numpy.sum(metrics, axis=0)))

    def net_io_counters(self):
        try:
            f = open("/proc/" + str(self.pid) + "/net/dev", "rt")
            lines = f.readlines()
        except IOError:
            return (0, 0)

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

class Process(dict):
    def __init__(self, pid):
        self.pid = pid
        self.proc = psutil.Process(pid)
        self.update(self.proc.as_dict(['pid', 'name', 'exe', 'cmdline']))
 
    def _update(self):
        self.update(self.proc.as_dict([
            'status', 'connections',
            'open_files', 'num_threads'])
        )

    def metrics(self):
        '''retrun metrics(cpu_percent, cpu_times_user, cpu_times_system,
                    memomy_percent, memory_rss, memory_vms,
                    io_counter_read, io_counter_write,
                    network_recv_bytes, network_send_bytes)'''
        try:
            proc = self.proc
            cpu_percent = proc.cpu_percent()
            cpu_times = proc.cpu_times()
            mem_percent = proc.memory_percent()
            mem_info = proc.memory_info()
        except psutil.AccessDenied:
            print 'Could not access /proc/%s are you root?' % self.pid
            dummpy = [0.0] * 10
            return Metrics(*dummpy)

        metrics = Metrics(
            cpu_percent=cpu_percent,
            cpu_times_user=cpu_times[0], 
            cpu_times_system=cpu_times[1],
            memory_percent=mem_percent, 
            memory_rss=mem_info[0], 
            memory_vms=mem_info[1],
            io_counter_read=0.0,
            io_counter_write=0.0,
            network_recv_bytes=0.0, 
            network_send_bytes=0.0,
        )
        self.update({'metrics': metrics})
        self._update()
        
        return metrics

    #def __str__(self):
    #    return str({'pid': self['pid'], 'status': self['status'], 'name': self['name']})

    def __repr__(self):
        return '<%s(pid=%i) at %s>' % (self.__class__.__name__, self.pid, id(self))
