import logging
import time
from threading import Lock

from common.address import Address
from conf import Conf
from log import Log
from state import State
from transport.communicator import Communicator
from transport.request import GetVoteRequest
from transport.response import GetVoteResponse

class Node:
    def __init__(self, node: Address, other_nodes: list[Address], conf: Conf = Conf()):
        self.conf = conf
        self.node: Address = node
        self.other_nodes = other_nodes

        self.state: State = State.FOLLOWER
        self.current_term = 0
        self.log = Log(self.current_term)
        self.voted_for: str | None = None
        self.votes_count = 0

        self.commit_index = 0
        self.last_applied = 0

        self.lock = Lock()

        self.election_deadline = self._get_time() + conf.get_election_timeout()
        self.communicator = Communicator(node, other_nodes, self._on_request_vote)

        logging.info(f"Node {node} successfully initialized")

    def run(self):
        while True:
            with self.lock:
                self._tick()
            time.sleep(0.05)

    def _tick(self):
        if self.state in (State.FOLLOWER, State.CANDIDATE):
            if self._get_time() > self.election_deadline:
                self.election_deadline = self._get_time() + self.conf.get_election_timeout()
                self.state = State.CANDIDATE
                self.voted_for = str(self.node)
                self.votes_count = 1
                self.current_term += 1

                responses = self.communicator.get_votes(GetVoteRequest(
                    node=str(self.node),
                    term=self.current_term,
                    last_log_index=self.log.get_last_log_index(),
                    last_log_term=self.log.get_last_log_term(),
                ))

                for response in responses:
                    if self.current_term == response.term and response.vote_granted:
                        self.votes_count += 1

                if self.votes_count > (len(self.other_nodes) + 1) / 2:
                    logging.info(f"Received {self.votes_count} votes, became LEADER, term {self.current_term}")
                    self.state = State.LEADER
                else:
                    logging.info(f"Received only {self.votes_count} votes, still CANDIDATE, term {self.current_term}")
    def _get_time(self):
        return time.time()

    def _on_request_vote(self, req: GetVoteRequest) -> GetVoteResponse:
        if self.lock.acquire(blocking=True, timeout=1.0):
            try:
                if self.current_term < req.term:
                    logging.info("Received request_vote with higher term, switch to FOLLOWER")
                    self.current_term = req.term
                    self.voted_for = None
                    self.state = State.FOLLOWER

                if self.state in (State.FOLLOWER, State.CANDIDATE):
                    if self.current_term == req.term:
                        if self.log.get_last_log_term() > req.last_log_term:
                            return GetVoteResponse(term=self.current_term, vote_granted=False)
                        elif self.log.get_last_log_term() == req.last_log_term and \
                            self.log.get_last_log_index() > req.last_log_index:
                            return GetVoteResponse(term=self.current_term, vote_granted=False)
                        elif self.voted_for is not None:
                            return GetVoteResponse(term=self.current_term, vote_granted=False)

                        self.voted_for = req.node
                        self.election_deadline = self._get_time() + self.conf.get_election_timeout()
                        return GetVoteResponse(term=self.current_term, vote_granted=True)

                return GetVoteResponse(term=self.current_term, vote_granted=False)
            finally:
                self.lock.release()
        else:
            return GetVoteResponse(term=self.current_term, vote_granted=False)
