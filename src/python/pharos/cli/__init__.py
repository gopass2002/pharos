import os
import sys

__all__ = ['cluster']

def progname(module, command):
    module_name = module.split(".")[-1]
    return '%s %s %s' % (os.path.basename(sys.argv[0]), module_name, command)

class CommandWrapper:
    def __init__(self, parser, func):
        self.parser = parser
        self.func = func
        self.doc = func.func_doc
        self.name = func.__name__
        self.module = func.__module__
        self.parser.description = func.func_doc
        self.parser.prog = progname(func.__module__, func.__name__)

    def call(self, args):
        optargs = self.parser.parse_args(args)
        self.func(optargs)


def cmd(parser):
    def decorator(func):
        return CommandWrapper(parser, func)
    return decorator
