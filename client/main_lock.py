import logging
import sys
import time

from client import Client
from common.zk_client import ZkClient

logging.basicConfig(level = logging.DEBUG, format = '%(asctime)s [%(levelname)s] %(message)s')

def main():
    watcher = ZkClient('127.0.0.1:2181')
    conf = watcher.get_conf()

    client = Client(conf)

    client_name = sys.argv[1]

    while True:
        op = input()
        if op == 'acq':
            args = ['lock', client_name, time.time()]
            print(client.lock_manage('acquire', args))
        elif op == 'pro':
            args = [client_name, time.time()]
            print(client.lock_manage('prolongate', args))
        elif op == 'rel':
            args = ['lock', client_name]
            print(client.lock_manage('release', args))
        else:
            print('Unknown operation')

if __name__ == '__main__':
    main()
