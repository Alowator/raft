import logging
import random
from typing import List

from common.address import Address

class Conf:
    def __init__(self, **kwargs):
        self.current_node: Address = kwargs.get('election_min_timeout', None)
        self.all_nodes: List[Address] = kwargs.get('election_min_timeout', [])

        self.election_min_timeout = kwargs.get('election_min_timeout', 3.0)
        self.election_max_timeout = kwargs.get('election_max_timeout', 5.0)

        self.append_entries_period = kwargs.get('append_entries_period', 1.0)

    @classmethod
    def instance(cls):
        if not hasattr(cls, 'singleton'):
            cls.singleton = Conf()
        return cls.singleton

    def get_address(self) -> Address:
        return self.current_node

    def get_election_timeout(self) -> float:
        return self.election_min_timeout + (self.election_max_timeout - self.election_min_timeout) * random.random()

    def get_append_entries_period(self) -> float:
        return self.append_entries_period

    def update(self, conf_dict: dict):
        for entry in conf_dict.items():
            setattr(self, entry[0], entry[1])

    def update_nodes(self, nodes: List[Address]):
        self.nodes = nodes

    def get_other_nodes(self) -> List[Address]:
        return [x for x in self.nodes if x != self.current_node]

    def get_all_nodes(self) -> List[Address]:
        return self.nodes
