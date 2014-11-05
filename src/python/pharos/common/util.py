import fcntl
import termios
import struct

def terminal_size():
    h, w, hp, wp = struct.unpack('HHHH',
        fcntl.ioctl(0, termios.TIOCGWINSZ,
        struct.pack('HHHH', 0, 0, 0, 0)))
    return w, h

def print_divider(char='-', highlight=False):
    max_w, max_h = terminal_size()
    print_line(char * max_w, highlight=highlight)

def print_line(line, highlight=False):
     max_w, max_h = terminal_size()
     if len(line) > max_w:
        if highlight:
            print '\033[1m' + line[:max_w] + '\033[0m'
        else:
            print line[:max_w]

     else:
        if highlight:
            print '\033[1m' + line + '\033[0m'
        else:
            print line

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
