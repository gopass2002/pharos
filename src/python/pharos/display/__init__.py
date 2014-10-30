import time
import requests
import curses, atexit
import numpy

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


class Top(Screen):
    def __init__(self, host, interval=1):
        Screen.__init__(self)
        self.interval = interval
        self.host = host

    def start_display(self):
        while True:
            try:
                res = requests.get(url='http://localhost:8008/node/%s/metrics' % self.host)
                if res.status_code != 200:
                    # TODO: implement-> handle error codes
                    print 'error'
                if res.json()['n'] == 0:
                    return
                self.containers = res.json()['containers']
                print self.containers
                self.lineno = 0
                self.refresh_screen()
                time.sleep(self.interval)
            except KeyboardInterrupt:
                break
    
    def header(self):
        metrics = [container['metrics'] for container in self.containers]
        templ = ' %-20s: %s'
        self.printer('RESOURCE USAGE SUMMARY', highlight=True)
        self.printer(templ % ('HOSTNAME', self.host))
        self.printer(templ % ('CONTAINERS', str(len(metrics))))
        
        # sum by column
        sum_metric = numpy.sum(metrics, axis=0)
        
        self.printer(templ % ('CPU', '%i%% (user: %i%% system: %i%%)' % (
            sum_metric[0], sum_metric[1], sum_metric[2])))
        self.printer(templ % ('MEMORY', '%i%% (rss: %s vms: %s)' % (
            sum_metric[3], bytes2human(sum_metric[4]), bytes2human(sum_metric[5]))))
        self.printer(templ % ('DISK IO', 'read: %s write: %s' % (
            bytes2human(sum_metric[5]), bytes2human(sum_metric[6]))))
        self.printer(templ % ('NETWROK', 'recv: %s sent: %s' % (
            bytes2human(sum_metric[7]), bytes2human(sum_metric[8]))))
        self.printer('')
        
    def body(self):
        containers = self.containers

        templ = '%15s %20s %30s %15s %6s %6s %15s %15s'
        header = ('CONTAINER_ID', 'IMAGE', 'NAME', 'STATUS', 'CPU %', 'MEM %', 'DISK', 'NETWORK')
        self.printer(templ % header, highlight=True)

        for con in containers:
            met = con['metrics']

            self.printer(templ % (
                con['id'][:10], con['image'][-20:], con['name'], con['status'],
                str(round(met[0], 2)) + '%', str(round(met[3], 2)) + '%',
                '%s/%s' % (bytes2human(met[5]), bytes2human(met[6])),
                '%s/%s' % (bytes2human(met[7]), bytes2human(met[8]))
                ))

    def footer(self):
        pass
