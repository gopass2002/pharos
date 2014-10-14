import os, sys
import encodings.idna
import numpy
import psutil
import docker
import pymongo

class PharosClient(object):
    def __init__(self, host='172.17.42.1', docker_port=2375, mongodb_port=27017):
        self.docker_c = docker.Client('tcp://%s:%i' % (host, docker_port))

    def containers(self):
        return [Container(status, self.docker_c) for status in self.docker_c.containers()]

    def kill_container(self, container):
        pass

    def stop_container(self, container):
        pass

    def inspect_container(self, container):
        pass

    def start_container(self, continer):
        pass

    def assign_ip_container(self, container):
        pass

class Container(object):
    def __init__(self, status, docker_client):
        self.docker_c =  docker_client
        self.id = status['Id']
        self.status = status['Status']
        self.name = status['Names'][0]
        self.image = status['Image']
    
    def pids(self):
        return [int(proc[1]) for proc in self.docker_c.top(self.id)['Processes']]

    def _get_process(self, pid):
        return Process(pid)

    def get_processes(self):
        return [self._get_process(pid) for pid in self.pids()]

    def get_metric(self):
        procs = self.get_processes()
        metrics = [proc.get_metric() for proc in procs]
        return numpy.sum(metrics, axis=0)

    def __str__(self):
        return str({'id': self.id, 'status': self.status, 'name': self.name, 'image': self.image})

    def __repr__(self):
        return self.__str__()

class Process(object):
    def __init__(self, pid):
        self.pid = pid
        self.proc = psutil.Process(pid)
        self.status = self.proc.status()
        self.cmdline = self.proc.cmdline()
        self.name = self.proc.name()
    
    def get_metric(self):
        try:
            proc = self.proc
            cpu_percent = proc.cpu_percent()
            cpu_times = proc.cpu_times()
            mem_percent = proc.memory_percent()
            mem_info = proc.memory_info()
            io_counters = proc.io_counters()
            net_counters = self.net_io_counters()
        except psutil.AccessDenied:
            print 'Could not access /proc/%s are you root?' % self.pid
            exit(1)

        metric = [
            cpu_percent, cpu_times[0], cpu_times[1],
            mem_percent, mem_info[0], mem_info[1],
            io_counters[2], io_counters[3],
            net_counters[0], net_counters[1]
        ]
        return tuple(metric)

    def net_io_counters(self):
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

