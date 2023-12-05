import logging
from functools import wraps

from common.response import SetResponse
from node import Node
from common.response import GetVoteResponse, AppendEntriesResponse
from common.request import GetVoteRequest, AppendEntriesRequest

def xmlrpc_income(func):
    @wraps(func)
    def wrapper(self, req):
        logging.debug(f"Income {req}")
        response = func(self, req)
        logging.debug(f"Outcome {response}")
        return response
    return wrapper

class Controller:
    def __init__(self):
        self.node = Node.instance()

    @classmethod
    def instance(cls):
        if not hasattr(cls, 'singleton'):
            cls.singleton = Controller()
        return cls.singleton

    @xmlrpc_income
    def get_vote(self, request: dict) -> GetVoteResponse:
        return self.node.on_get_vote(GetVoteRequest(**request))

    @xmlrpc_income
    def append_entries(self, request: dict) -> AppendEntriesResponse:
        return self.node.on_append_entries(AppendEntriesRequest(**request))

    @xmlrpc_income
    def set(self, value: str) -> SetResponse:
        return self.node.on_set(value)
