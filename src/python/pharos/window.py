import json, os, sys, string, time
import requests
import curses, atexit
import psutil
from numpy import array
from datetime import datetime, timedelta

from .common import (
    get_preference
)

from .common import (
    LIGHTTOWER_HOST,
    LIGHTTOWER_REMOTE_API_PORT,
)

class Screen(object):
    def __init__(self, console=False):
        self.console = console
        if not console:
            self.win = curses.initscr()
            self.lineno = 0
            atexit.register(self.tear_down)
            curses.endwin()
            self.printer = self.print_window
        else:
            self.printer = self.print_console

    def tear_down(self):
        self.win.keypad(0)
        curses.nocbreak()
        curses.echo()
        curses.endwin()

    def print_window(self, line, highlight=False):
        win = self.win
        try:
            if highlight:
                line += ' ' * (win.getmaxyx()[1] - len(line))
                win.addstr(self.lineno, 0, line, curses.A_REVERSE)
            else:
                win.addstr(self.lineno, 0, line, 0)
        except curses.error:
            self.lineno = 0
            win.refresh()
        else:
            self.lineno += 1

    def print_console(self, line, highlight=False):
        if highlight:
            print '\033[1m' + line + '\033[0m'
        else:
            print line

    def refresh_screen(self):
        self.lineno = 0
        
        if not self.console:
            curses.endwin()
            self.win.erase()
        
        self.header()
        self.body()
        self.footer()

        if not self.console:
            self.win.refresh()

    def header(self):
        pass

    def body(self):
        pass

    def footer(self):
        pass

def bytes2human(n, postfix=''):
    symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i + 1) * 10
    for s in reversed(symbols):
        if n >= prefix[s]:
            value = int(float(n) / prefix[s])
            return '%s%s%s' % (value, s, postfix)
    return '%sB%s' % (n, postfix)


class NodeTop(Screen):
    def __init__(self, host, interval=1):
        Screen.__init__(self, console=True)
        self.interval = interval
        self.host = host
        self.node_metrics_before = None
        self.container_metrics_before = {}

    def start_display(self):
        remote_url = 'http://%s:%i/node/%s/metrics' % (
            get_preference(LIGHTTOWER_HOST),
            get_preference(LIGHTTOWER_REMOTE_API_PORT),
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
                print self.node['metrics']
                self.containers = self.node['containers']
                self.lineno = 0
                self.refresh_screen()
                time.sleep(self.interval)
            except KeyboardInterrupt:
                break
    
    def header(self):
        metrics = self.node['metrics']
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
            str(round(metrics[1], 2)), str(round(metrics[2], 2))))
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

        templ = '%15s %20s %20s %6s %6s %15s %15s'
        header = ('CONTAINER_ID', 'IMAGE', 'NAME', 'CPU', 'MEM', 'DISK', 'NETWORK')
        self.printer(templ % header, highlight=True)
        
        for container in containers:
            delta = None
            metrics = container['metrics']
            if container['Id'] in self.container_metrics_before:
                before = self.container_metrics_before[container['Id']]
                delta = array(metrics) - array(before)
            else:
                delta = [0.0] * 10
            self.container_metrics_before[container['Id']] = metrics

            self.printer(templ % (
                container['Id'][:10], container['Config']['Image'][-20:], container['Name'],
                str(round(metrics[0], 2)) + '%', str(round(metrics[3], 2)) + '%',
                '%s/%s' % (bytes2human(long(delta[5])), bytes2human(long(delta[6]))),
                '%s/%s' % (bytes2human(long(delta[7])), bytes2human(long(delta[8])))
                )
            )
        

    def footer(self):
        pass

class ContainerTop(Screen):
    def __init__(self, host, interval=1):
        Screen.__init__(self, console=True)
        self.interval = interval
        self.host = host
        self.node_metrics_before = None
        self.container_metrics_before = {}

    def start_display(self):
        remote_url = 'http://%s:%i/node/%s/metrics' % (
            get_preference(LIGHTTOWER_HOST),
            get_preference(LIGHTTOWER_REMOTE_API_PORT),
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
                print self.node['metrics']
                self.containers = self.node['containers']
                self.lineno = 0
                self.refresh_screen()
                time.sleep(self.interval)
            except KeyboardInterrupt:
                break
    
    def header(self):
        metrics = self.node['metrics']
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
            str(round(metrics[1], 2)), str(round(metrics[2], 2))))
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

        templ = '%15s %20s %20s %6s %6s %15s %15s'
        header = ('CONTAINER_ID', 'IMAGE', 'NAME', 'CPU', 'MEM', 'DISK', 'NETWORK')
        self.printer(templ % header, highlight=True)
        
        for container in containers:
            delta = None
            metrics = container['metrics']
            if container['Id'] in self.container_metrics_before:
                before = self.container_metrics_before[container['Id']]
                delta = array(metrics) - array(before)
            else:
                delta = [0.0] * 10
            self.container_metrics_before[container['Id']] = metrics

            self.printer(templ % (
                container['Id'][:10], container['Config']['Image'][-20:], container['Name'],
                str(round(metrics[0], 2)) + '%', str(round(metrics[3], 2)) + '%',
                '%s/%s' % (bytes2human(long(delta[5])), bytes2human(long(delta[6]))),
                '%s/%s' % (bytes2human(long(delta[7])), bytes2human(long(delta[8])))
                )
            )
        

    def footer(self):
        pass
