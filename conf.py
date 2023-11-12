import random

class Conf:

    def __init__(self, **kwargs):
        self.election_min_timeout = kwargs.get('election_min_timeout', 1.0)
        self.election_max_timeout = kwargs.get('election_max_timeout', 2.0)

    def get_election_timeout(self) -> float:
        return self.election_min_timeout + (self.election_max_timeout - self.election_min_timeout) * random.random()
