import argparse
import sys
import _cli

commands = {}


def load_commands():
    for name in _cli.__all__:
        __import__('pharos._cli.%s' % name)
        mod = getattr(_cli, name)
        for member in dir(getattr(_cli, name)):
            attr = getattr(mod, member)
            if isinstance(attr,_cli.CommandWrapper):
                commands[member] = attr


def print_help():
    print '\nUsage: pharos COMMAND [arg...]\n'
    print 'Commands:'
    for func in commands.values():
        print '%-20s: %s' % (func.name, func.doc)


def run_cmd(args):
    if args[0] not in commands:
        print_help()
    else:
        func = commands[args[0]]
        func.call(args[1:])

def main():
    load_commands()

    if len(sys.argv) < 2:
        print_help()
    else:
        run_cmd(sys.argv[1:])


if __name__ == '__main__':
    main()
