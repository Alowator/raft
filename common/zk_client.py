import json
import logging
import time

from kazoo.client import KazooClient
from kazoo.protocol.states import WatchedEvent

from common.address import Address
from common.conf import Conf

class ZkClient():
    CONF_PATH = '/cluster'

    def __init__(self, zk_host: str):
        self.zk = KazooClient(hosts=zk_host)
        self.zk.start()

        self.conf = Conf.instance()
        self._update_conf()
        self._update_nodes()

    def _watch(self, event: WatchedEvent):
        if event.path == self.CONF_PATH and event.type == 'CHANGED':
            self._update_conf()
        elif event.path == self.CONF_PATH and event.type == 'CHILD':
            self._update_nodes()
        else:
            logging.error(f"Unknown event from ZooKeeper: {event}")
            self._update_conf()
            self._update_nodes()

    def _update_conf(self):
        try:
            value = self.zk.get(self.CONF_PATH, watch=self._watch)
            conf_dict = json.loads(value[0])
            logging.info(f"Configuration update {conf_dict}")
            self.conf.update(conf_dict)
        except Exception as exc:
            logging.error(f"While updating conf: {exc}, will try again in 60 second")
            time.sleep(60)
            self._update_conf()

    def _update_nodes(self):
        try:
            value = self.zk.get_children(self.CONF_PATH, watch=self._watch, include_data=False)
            logging.info(f"Children update {value}")
            self.conf.update_nodes([Address(*x.split(':')) for x in value])
        except Exception as exc:
            logging.error(f"While updating children: {exc}, will try again in 60 second")
            time.sleep(60)
            self._update_nodes()

    def get_conf(self) -> Conf:
        return self.conf
