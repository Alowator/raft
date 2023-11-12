import logging
import xmlrpc.client
from threading import Thread
from typing import List, Dict
from xmlrpc.server import SimpleXMLRPCServer

from common.address import Address
from transport.request import GetVoteRequest
from transport.response import GetVoteResponse

class Communicator:
    def __init__(self, current_node: Address, nodes: List[Address], request_vote_callback):
        self.current_node = current_node
        self.nodes = nodes

        self.request_vote_callback = request_vote_callback

        self._server = SimpleXMLRPCServer(current_node.tuple(), allow_none=True, logRequests=False)
        self._server.register_function(self._get_vote_income, "get_vote")

        self._thread = Thread(target=self._run, daemon=True)
        self._thread.start()

    def get_votes(self, req: GetVoteRequest) -> List[GetVoteResponse]:
        result = []
        logging.debug(f"Send {req} to {self.nodes}")
        for node in self.nodes:
            with xmlrpc.client.ServerProxy(node.get_http_url()) as proxy:
                try:
                    response_dict = proxy.get_vote(req)
                    logging.debug(f"Received {response_dict} from {node}")
                    result.append(GetVoteResponse(**response_dict))
                except ConnectionError as exc:
                    logging.warning(exc)
        return result

    def _get_vote_income(self, req: dict) -> Dict:
        return self.request_vote_callback(GetVoteRequest(**req)).dict()

    def _run(self):
        logging.info(f"Server listening on {self.current_node}")
        self._server.serve_forever()
