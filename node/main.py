import logging
import sys

from common.address import Address
from node import Node
from watcher import Watcher

logging.basicConfig(level = logging.DEBUG, format = '%(asctime)s [%(levelname)s] %(message)s')

def main():
    watcher = Watcher('127.0.0.1:2181')
    conf = watcher.get_conf()

    node = Node(Address('127.0.0.1', sys.argv[1]), conf)
    node.run()

if __name__ == '__main__':
    main()
