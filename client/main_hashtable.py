import logging

from client import Client
from common.zk_client import ZkClient

logging.basicConfig(level = logging.DEBUG, format = '%(asctime)s [%(levelname)s] %(message)s')

def main():
    watcher = ZkClient('127.0.0.1:2181')
    conf = watcher.get_conf()

    client = Client(conf)

    while True:
        op = input()
        if op == 'set':
            key = input()
            value = input()
            client.set(key, value)
        elif op == 'get':
            key = input()
            print(client.get(key))
        else:
            print('Unknown operation')

if __name__ == '__main__':
    main()
