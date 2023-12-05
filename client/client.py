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

    def set(self, value):
        node = self._get_node()
        response = self._set(value, node)
        while response.success == False:
            if response.redirect_to is not None:
                self.last_leader = Address(*response.redirect_to.split(':'))
            else:
                self.last_leader = None
            response = self._set(value, self.last_leader)

    def _set(self, value, node) -> SetResponse:
        with xmlrpc.client.ServerProxy(node.get_http_url()) as proxy:
            try:
                logging.debug(f"Send {value} to {node}")
                response = proxy.set(value)
                logging.debug(f"Received {response} from {node}")
                return SetResponse(**response)
            except BaseException as exc:
                logging.warning(f"Error while connecting to {node}: {exc}")
                raise exc

    def _get_node(self) -> Address:
        if self.last_leader is None:
            self.last_leader = random.choice(self.conf.get_all_nodes())
        return self.last_leader
