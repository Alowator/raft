import logging
import xmlrpc.client
from concurrent.futures import ThreadPoolExecutor, Executor, Future
from functools import wraps

from common.address import Address
from common.request import GetVoteRequest, AppendEntriesRequest
from common.response import GetVoteResponse, AppendEntriesResponse

def xmlrpc_call(func):
    @wraps(func)
    def wrapper(self, node, req):
        with xmlrpc.client.ServerProxy(node.get_http_url(), allow_none=True) as proxy:
            try:
                logging.debug(f"Send {req} to {node}")
                response = func(self, proxy, req)
                logging.debug(f"Received {response} from {node}")
                return response
            except BaseException as exc:
                logging.warning(f"Error while connecting to {node}: {exc}")
                raise exc

    return wrapper

class Communicator:
    def __init__(self):
        self.executor: Executor = ThreadPoolExecutor(max_workers=10)

    def get_votes(self, req: GetVoteRequest, nodes):
        return [self.executor.submit(self._get_vote, node, req) for node in nodes]

    def append_entries(self, req: AppendEntriesRequest, node: Address) -> Future[AppendEntriesResponse]:
        return self.executor.submit(self._append_entries, node, req)

    @xmlrpc_call
    def _get_vote(self, proxy, req: GetVoteRequest) -> GetVoteResponse:
        return GetVoteResponse(**proxy.get_vote(req))

    @xmlrpc_call
    def _append_entries(self, proxy, req: AppendEntriesRequest) -> AppendEntriesResponse:
        return AppendEntriesResponse(**proxy.append_entries(req))
