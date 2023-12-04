import logging

from client import Client

logging.basicConfig(level = logging.DEBUG, format = '%(asctime)s [%(levelname)s] %(message)s')

def main():
    client = Client('127.0.0.1:2181')
    client.set('value')

if __name__ == '__main__':
    main()
