import logging
import time
import xmlrpc.client
from typing import List

from kazoo.client import KazooClient
from kazoo.protocol.states import WatchedEvent

from common.address import Address

class Client:
    CONF_PATH = '/cluster'

    def __init__(self, zk_host: str):
        self.zk = KazooClient(hosts=zk_host)
        self.zk.start()

        self.available_nodes: List[Address] = []

        self._update_nodes()
        if len(self.available_nodes) == 0:
            raise AttributeError("There are no nodes")

    def set(self, value):
        node = self.get_node()
        with xmlrpc.client.ServerProxy(node.get_http_url()) as proxy:
            try:
                response_dict = proxy.set(value)
                logging.debug(f"Received {response_dict} from {node}")
                # return GetVoteResponse(**response_dict)
            except BaseException as exc:
                logging.warning(f"Error while connecting to {node}: {exc}")
                raise exc

    def get_node(self) -> Address:
        return self.available_nodes[0]

    def _watch(self, event: WatchedEvent):
        if event.path == self.CONF_PATH and event.type == 'CHILD':
            self._update_nodes()
        else:
            logging.error(f"Unknown event from ZooKeeper: {event}")
            self._update_nodes()

    def _update_nodes(self):
        try:
            value = self.zk.get_children(self.CONF_PATH, watch=self._watch, include_data=False)
            self.available_nodes = [Address(*x.split(':')) for x in value]
            logging.info(f"Nodes update {self.available_nodes}")
        except Exception as exc:
            logging.error(f"While updating children: {exc}, will try again in 60 second")
            time.sleep(10)
            self._update_nodes()
