import logging
import random
import xmlrpc.client

from common.address import Address
from common.conf import Conf
from common.response import SetResponse

class Client:
    def __init__(self, conf: Conf):
        self.conf = conf
        self.last_leader = None

    def set(self, key, value):
        node = self._get_node()
        response = self._set(key, value, node)
        while response.success == False:
            if response.redirect_to is not None:
                self.last_leader = Address(*response.redirect_to.split(':'))
            else:
                self.last_leader = None
                self.last_leader = self._get_node()
            response = self._set(key, value, self.last_leader)

    def get(self, key):
        node = self._get_node()
        with xmlrpc.client.ServerProxy(node.get_http_url()) as proxy:
            try:
                return proxy.get(key)
            except BaseException as exc:
                logging.warning(f"Error while connecting to {node}: {exc}")

    def _set(self, key, value, node) -> SetResponse:
        with xmlrpc.client.ServerProxy(node.get_http_url()) as proxy:
            try:
                logging.debug(f"Send {value} to {node}")
                response = proxy.set(key, value)
                logging.debug(f"Received {response} from {node}")
                return SetResponse(**response)
            except BaseException as exc:
                logging.warning(f"Error while connecting to {node}: {exc}")
                return SetResponse(success=False, redirect_to=None, res=None)

    def _get_node(self) -> Address:
        if self.last_leader is None:
            self.last_leader = random.choice(self.conf.get_all_nodes())
        return self.last_leader

    def lock_manage(self, method, args):
        node = self._get_node()
        response = self._lock_manage(method, args, node)
        while response.success == False:
            if response.redirect_to is not None:
                self.last_leader = Address(*response.redirect_to.split(':'))
            else:
                self.last_leader = None
                self.last_leader = self._get_node()
            response = self._lock_manage(method, args, self.last_leader)
        return response

    def _lock_manage(self, method, args, node):
        with xmlrpc.client.ServerProxy(node.get_http_url()) as proxy:
            try:
                response = proxy.lock_manage(method, args)
                logging.debug(f"Received {response} from {node}")
                return SetResponse(**response)
            except BaseException as exc:
                logging.warning(f"Error while connecting to {node}: {exc}")
                return SetResponse(success=False, redirect_to=None, res=None)
