import argparse
import os
import pharos.cli
import pymongo
from pharos.cli import cmd

top_parser = argparse.ArgumentParser()
top_parser.add_argument('host', help='target host to display')
@cmd(top_parser)
def top(args):
    'display <host> container\'s metrics'
    host = args.host
    c = pymongo.MongoClient('localhost', 27017)
    col = c.pharos.metrics

    q = {'hostname': host}
    metrics = list(col.find(q))
    print metrics
