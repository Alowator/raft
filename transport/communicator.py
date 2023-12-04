import logging
import xmlrpc.client
from concurrent.futures import ThreadPoolExecutor, Executor, Future
from threading import Thread
from typing import List, Dict
from xmlrpc.server import SimpleXMLRPCServer

from common.address import Address
from conf import Conf
from transport.request import GetVoteRequest, AppendEntriesRequest
from transport.response import GetVoteResponse, AppendEntriesResponse

class Communicator:
    def __init__(self, current_node: Address, conf: Conf, request_vote_callback, append_entries_callback,
                 set_value_callback):
        self.current_node = current_node
        self.conf = conf

        self.request_vote_callback = request_vote_callback
        self.append_entries_callback = append_entries_callback
        self.set_value_callback = set_value_callback

        self._server = SimpleXMLRPCServer(current_node.tuple(), allow_none=True, logRequests=False)
        self._server.register_function(self._get_vote_income, "get_vote")
        self._server.register_function(self._append_entries_income, "append_entries")
        self._server.register_function(self._set_value, "set")

        self.executor: Executor = ThreadPoolExecutor(max_workers=10)

        self._thread = Thread(target=self._run, daemon=True)
        self._thread.start()

    def get_votes(self, req: GetVoteRequest) -> List[Future[GetVoteResponse]]:
        nodes = self.conf.get_nodes()
        logging.debug(f"Send {req} to {nodes}")
        return [self.executor.submit(self._get_vote, node, req) for node in nodes]

    def _get_vote(self, node: Address, req: GetVoteRequest) -> GetVoteResponse:
        with xmlrpc.client.ServerProxy(node.get_http_url()) as proxy:
            try:
                response_dict = proxy.get_vote(req)
                logging.debug(f"Received {response_dict} from {node}")
                return GetVoteResponse(**response_dict)
            except BaseException as exc:
                logging.warning(f"Error while connecting to {node}: {exc}")
                raise exc

    def append_entries(self, node: Address, req: AppendEntriesRequest) -> Future[AppendEntriesResponse]:
        logging.debug(f"Send {req} to {node}")
        return self.executor.submit(self._append_entries, node, req)

    def _append_entries(self, node: Address, req: AppendEntriesRequest) -> AppendEntriesResponse:
        with xmlrpc.client.ServerProxy(node.get_http_url(), allow_none=True) as proxy:
            try:
                response_dict = proxy.append_entries(req)
                logging.debug(f"Received {response_dict} from {node}")
                return AppendEntriesResponse(**response_dict)
            except BaseException as exc:
                logging.warning(f"Error while connecting to {node}: {exc}")
                raise exc

    def _get_vote_income(self, req: dict) -> Dict:
        logging.debug(f"Received GetVoteRequest{req}")
        return self.request_vote_callback(GetVoteRequest(**req)).dict()

    def _append_entries_income(self, req: dict) -> Dict:
        logging.debug(f"Received AppendEntriesRequest{req}")
        return self.append_entries_callback(AppendEntriesRequest(**req)).dict()

    def _set_value(self, value: str):
        logging.debug(f"Received _set_value {value}")
        self.set_value_callback(value)

    def _run(self):
        logging.info(f"Server listening on {self.current_node}")
        self._server.serve_forever()
