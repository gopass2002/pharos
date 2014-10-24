import pharos.rest as rest
import argparse, sys

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8008, help='specify port')
    args = parser.parse_args(sys.argv[1:])
    
    for name in rest.__VIEWS__:
        __import__('pharos.rest.%s' % name)
    rest.app.run(host='0.0.0.0', port=args.port, debug=True)
