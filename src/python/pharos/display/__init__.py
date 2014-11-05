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

