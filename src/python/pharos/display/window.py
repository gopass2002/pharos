import json, os, sys, string, time
import requests
import curses, atexit
import re
from datetime import datetime, timedelta

import psutil
from numpy import array

from . import Screen
from pharos.common.util import bytes2human
import pharos.config as Config

class NodeTop(Screen):
    def __init__(self, host, interval=1, console=False):
        Screen.__init__(self, console=console)
        self.interval = interval
        self.host = host
        self.node_metrics_before = None
        self.container_metrics_before = {}

    def start_display(self):
        remote_url = 'http://%s:%i/nodes/%s/metrics' % (
            Config.get_preference(Config.LIGHTTOWER_HOST),
            Config.get_preference(Config.LIGHTTOWER_REMOTE_API_PORT),
            self.host
        )
        print remote_url
        while True:
            try:
                res = requests.get(url=remote_url)
                if res.status_code != 200:
                    # TODO: implement-> handle error codes
                    print 'error'
                
                self.node = res.json()
                self.containers = self.node['Containers']
                self.lineno = 0
                self.refresh_screen()
                time.sleep(self.interval)
            except KeyboardInterrupt:
                break
    
    def header(self):
        metrics = self.node['Metrics']
        templ = ' %-20s: %s'
        self.printer('RESOURCE USAGE SUMMARY', highlight=True)
        self.printer(templ % ('HOSTNAME', self.host))
        self.printer(templ % ('CONTAINERS', str(len(self.containers))))
        
        delta = None
        if self.node_metrics_before:
            delta = array(metrics) - array(self.node_metrics_before)
        else:
            delta = [0.0] * 10
        self.node_metrics_before = metrics
        self.printer(templ % ('CPU', '%s%% (user: %s%% system: %s%%)' % (
            str(round(metrics[0], 2)), 
            str(round(metrics[1]/100, 2)), str(round(metrics[2]/100, 2))))
        )

        self.printer(templ % ('MEMORY', '%s%% (rss: %s vms: %s)' % (
                str(round(metrics[3], 2)), 
                bytes2human(int(metrics[4])), bytes2human(int(metrics[5]))
            ))
        )

        self.printer(templ % ('DISK IO', 'read: %s(%s/sec) write: %s(%s/sec)' % (
                bytes2human(int(metrics[5])), bytes2human(int(delta[5])), 
                bytes2human(int(metrics[6])), bytes2human(int(delta[6]))
            ))
        )

        self.printer(templ % ('NETWROK', 'recv: %s(%s/sec) sent: %s(%s/sec)' % (
                bytes2human(int(metrics[7])), bytes2human(int(delta[7])),
                bytes2human(int(metrics[8])), bytes2human(int(delta[8]))
            ))
        )
        self.printer('')
        
        
    def body(self):
        containers = self.containers

        templ = '%15s %30s %30s %6s %6s %15s %15s'
        header = ('CONTAINER_ID', 'IMAGE', 'NAME', 'CPU', 'MEM', 'DISK', 'NETWORK')
        self.printer(templ % header, highlight=True)
        
        for container in containers:
            delta = None
            metrics = container['Metrics']
            if container['Id'] in self.container_metrics_before:
                before = self.container_metrics_before[container['Id']]
                delta = array(metrics) - array(before)
            else:
                delta = [0.0] * 10
            self.container_metrics_before[container['Id']] = metrics

            self.printer(templ % (
                container['Id'][:10], container['Image'][-25:], container['Name'][1:],
                str(round(metrics[0], 2)) + '%', str(round(metrics[3], 2)) + '%',
                '%s/%s' % (bytes2human(long(delta[5])), bytes2human(long(delta[6]))),
                '%s/%s' % (bytes2human(long(delta[7])), bytes2human(long(delta[8])))
                )
            )
        

    def footer(self):
        pass

class ContainerTop(Screen):
    def __init__(self, container_id, interval=1, console=False):
        Screen.__init__(self, console=console)
        self.interval = interval
        self.container_id = container_id
        self.container_metrics_before = None
        self.process_metrics_before = {}

    def start_display(self):
        remote_url = 'http://%s:%i/containers/%s/metrics' % (
            Config.get_preference(Config.LIGHTTOWER_HOST),
            Config.get_preference(Config.LIGHTTOWER_REMOTE_API_PORT),
            self.container_id
        )
        while True:
            try:
                res = requests.get(url=remote_url)
                if res.status_code != 200:
                    # TODO: implement-> handle error codes
                    print 'error'
                
                self.container = res.json()
                self.lineno = 0
                self.refresh_screen()
                time.sleep(self.interval)
            except KeyboardInterrupt:
                break
    
    def header(self):
        metrics = self.container['Metrics']
        templ = ' %-20s: %s'
        self.printer('CONTAINER RESOURCE USAGE SUMMARY', highlight=True)
        self.printer(templ % ('CONTAINER ID', self.container['Id']))
        self.printer(templ % ('PROCESSES', str(len(self.container['Processes']))))
        
        delta = None
        if self.container_metrics_before:
            delta = array(metrics) - array(self.container_metrics_before)
        else:
            delta = [0.0] * 10
        self.container_metrics_before = metrics
        self.printer(templ % ('CPU', '%s%% (user: %s%% system: %s%%)' % (
            str(round(metrics[0], 2)), 
            str(round(metrics[1]/100, 2)), str(round(metrics[2]/100, 2))))
        )

        self.printer(templ % ('MEMORY', '%s%% (rss: %s vms: %s)' % (
                str(round(metrics[3], 2)), 
                bytes2human(int(metrics[4])), bytes2human(int(metrics[5]))
            ))
        )

        self.printer(templ % ('DISK IO', 'read: %s(%s/sec) write: %s(%s/sec)' % (
                bytes2human(int(metrics[5])), bytes2human(int(delta[5])), 
                bytes2human(int(metrics[6])), bytes2human(int(delta[6]))
            ))
        )

        self.printer(templ % ('NETWROK', 'recv: %s(%s/sec) sent: %s(%s/sec)' % (
                bytes2human(int(metrics[7])), bytes2human(int(delta[7])),
                bytes2human(int(metrics[8])), bytes2human(int(delta[8]))
            ))
        )
        self.printer('')
        
        
    def body(self):
        processes = self.container['Processes']

        templ = '%-6s %-7s %-7s %-6s %-6s %-5s %-25s'
        header = ('PID', 'VIRT', 'RES', 'CPU%', 'MEM%', 'TASKS', 'COMMAND LINE')
        self.printer(templ % header, highlight=True)
        
        for proc in processes:
            delta = None
            metrics = proc['metrics']
            if proc['pid'] in self.process_metrics_before:
                before = self.process_metrics_before[proc['pid']]
                delta = array(metrics) - array(before)
            else:
                delta = [0.0] * 10
            self.process_metrics_before[proc['pid']] = metrics

            self.printer(templ % (
                str(proc['pid']), bytes2human(long(metrics[5])), bytes2human(long(metrics[4])),
                str(round(metrics[0], 2)) + '%', str(round(metrics[3], 2)) + '%',
                str(proc['num_threads']), ' '.join(proc['cmdline'])
                )
            )
        self.printer('')
        

    def footer(self):
        self.printer('CONTAINER INFOMATION', highlight=True)
        templ = '%-10s: %-20s %-10s: %-20s'
        created = datetime(*map(int, re.split('[^\d]', self.container['Created'][:-4])[:-1]))
        started = datetime(*map(int, re.split('[^\d]', self.container['Started'][:-4])[:-1]))
        
        self.printer(templ % ('HOST', self.container['Host'], 'IMAGE', self.container['Image']))
        self.printer(templ % ('CREATED', created, 'STARTED', started))
        self.printer('%-10s: %-20s' % ('COMMAND', ' '.join(self.container['Command'])))


