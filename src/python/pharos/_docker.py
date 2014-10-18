import docker
import psutil
import numpy

__all__ = [
    # classes
    'Container', 'Process'
]

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
        return [Process(pid) for pid in self.pids()]

    def metrics(self, processes=None):
        if not processes:
            processes = self.processes()
        metrics = [process.metrics() for process in processes]
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
