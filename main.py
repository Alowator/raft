import logging

from common.address import Address
from node import Node

logging.basicConfig(level = logging.WARN, format = '%(asctime)s [%(levelname)s] %(message)s')

def main():
    node = Node(
        Address('127.0.0.1', 5432),
        [Address('127.0.0.1', 5431), Address('127.0.0.1', 5430)]
    )
    node.run()

if __name__ == '__main__':
    main()
