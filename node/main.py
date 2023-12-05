import logging
import sys

from common.address import Address
from common.zk_client import ZkClient
from node import Node
from server import Server

logging.basicConfig(level = logging.DEBUG, format = '%(asctime)s [%(levelname)s] %(message)s')

def main():
    watcher = ZkClient('127.0.0.1:2181')
    conf = watcher.get_conf()
    conf.current_node = Address('127.0.0.1', sys.argv[1])

    server = Server(conf.get_address())
    server.serve()

    Node.instance().run()

if __name__ == '__main__':
    main()
