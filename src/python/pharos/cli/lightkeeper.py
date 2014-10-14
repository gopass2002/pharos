import argparse
import pharos.cli
import os
from pharos.cli import cmd

run_parser = argparse.ArgumentParser()
run_parser.add_argument('-d', '--docker', action='store_true', help='run docker daemon')
@cmd(run_parser)
def run(args):
    'run lightkeeper daemons'
    cmd = 'docker run -d --privileged=true -v /proc:/pharos/proc pharos'
    print cmd
    os.system(cmd)
