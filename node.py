import logging
import time
from concurrent.futures import Future
from threading import Lock
from typing import List

from common.address import Address
from conf import Conf
from log import Log
from state import State
from transport.communicator import Communicator
from transport.request import GetVoteRequest, AppendEntriesRequest
from transport.response import GetVoteResponse, AppendEntriesResponse

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

        self.next_index = {}
        self.match_index = {}

        self.lock = Lock()

        self.election_deadline = self._get_time() + conf.get_election_timeout()
        self.append_entries_deadline = .0
        self.communicator = Communicator(node, other_nodes, self._on_request_vote, self._on_append_entries)
        self.request_vote_futures: List[Future[GetVoteResponse]] = []
        self.append_entries_futures: List[Future[AppendEntriesResponse]] = []

        logging.info(f"Node {node} successfully initialized")

    def run(self):
        while True:
            with self.lock:
                self._tick()
            time.sleep(0.1)

    def _tick(self):
        if self.state in (State.FOLLOWER, State.CANDIDATE):
            if self._get_time() > self.election_deadline:
                self.election_deadline = self._get_time() + self.conf.get_election_timeout()
                self.state = State.CANDIDATE
                self.voted_for = str(self.node)
                self.votes_count = 1
                self.current_term += 1

                self.request_vote_futures = self.communicator.get_votes(GetVoteRequest(
                    node=str(self.node),
                    term=self.current_term,
                    last_log_index=self.log.get_last_log_index(),
                    last_log_term=self.log.get_last_log_term(),
                ))

        if self.state == State.CANDIDATE:
            undone_futures = []
            for future in self.request_vote_futures:
                if future.done():
                    if future.exception() is None:
                        response = future.result()
                        if response.vote_granted:
                            self.votes_count += 1
                else:
                    undone_futures.append(future)

            self.request_vote_futures = undone_futures

            if self.votes_count > (len(self.other_nodes) + 1) / 2:
                logging.info(f"Received {self.votes_count} votes, became LEADER, term {self.current_term}")
                self.state = State.LEADER
                for node in map(str, self.other_nodes):
                    self.next_index[node] = self.log.get_last_log_index() + 1
                    self.match_index[node] = 0

        if self.state == State.LEADER:
            if self._get_time() > self.append_entries_deadline:
                self.append_entries_deadline = self._get_time() + self.conf.append_entries_period
                for node in self.other_nodes:
                    next_node_index = self.next_index[str(node)]
                    if next_node_index <= self.log.get_last_log_index():
                        entry = self.log.get_entry(next_node_index)
                        # self.next_index[str(node)] = entry.get_index() + 1
                    else:
                        entry = None

                    value = None if entry is None else entry.get_value()
                    append_entries_future = self.communicator.append_entries(node, AppendEntriesRequest(
                        node=str(self.node),
                        term=self.current_term,
                        prev_log_index=self.log.get_entry(next_node_index - 1).get_index(),
                        prev_log_term=self.log.get_entry(next_node_index - 1).get_term(),
                        entry=value,
                        leader_commit=self.commit_index,
                    ))
                    self.append_entries_futures.append(append_entries_future)

            undone_append_entries_futures = []
            for append_entries_future in self.append_entries_futures:
                if append_entries_future.done():
                    if append_entries_future.exception() is None:
                        response = append_entries_future.result()
                        if self.current_term < response.term:
                            self.current_term = response.term
                            self.state = State.FOLLOWER
                            logging.info(f"Received append_entries_response with term {response.term}, switch to FOLLOWER")
                        elif response.success:
                            self.match_index[response.node] = max(self.match_index[response.node], self.next_index[response.node])
                            if self.next_index[response.node] <= self.log.get_last_log_index():
                                self.next_index[response.node] += 1
                        else:
                            self.next_index[response.node] -= 1

                else:
                    undone_append_entries_futures.append(append_entries_future)
            self.append_entries_futures = undone_append_entries_futures

            for node1 in map(str, self.other_nodes):
                commit_index_candidate  = self.match_index[node1]
                votes = 0
                for node2 in map(str, self.other_nodes):
                    if commit_index_candidate >= self.match_index[node2]:
                        votes += 1

                if votes >= (len(self.other_nodes) + 1) // 2 and commit_index_candidate > self.commit_index:
                    self.commit_index = commit_index_candidate

    def _get_time(self):
        return time.time()

    def _on_request_vote(self, req: GetVoteRequest) -> GetVoteResponse:
        with self.lock:
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

    def _on_append_entries(self, req: AppendEntriesRequest) -> AppendEntriesResponse:
        with self.lock:
            if self.current_term > req.term:
                return AppendEntriesResponse(node=str(self.node), term=self.current_term, success=False)

            self.election_deadline = self._get_time() + self.conf.get_election_timeout()
            self.current_term = req.term

            if self.log.contains(req.prev_log_index):
                if self.log.get_entry(req.prev_log_index).get_term() == req.prev_log_term:
                    if req.entry is not None:
                        if self.log.contains(req.prev_log_index + 1):
                            logging.warning("Log record with index already exists, maybe leader sent record TWICE")
                            self.log.truncate_from(req.prev_log_index + 1)
                        self.log.add(req.entry, self.current_term)
                        if self.commit_index < req.leader_commit:
                            self.commit_index = min(req.leader_commit, self.log.get_last_log_index())
                    return AppendEntriesResponse(node=str(self.node), term=self.current_term, success=True)
                else:
                    self.log.truncate_from(req.prev_log_index)
                    if self.commit_index < req.leader_commit:
                        self.commit_index = min(req.leader_commit, self.log.get_last_log_index())
                    return AppendEntriesResponse(node=str(self.node), term=self.current_term, success=False)
            else:
                return AppendEntriesResponse(node=str(self.node), term=self.current_term, success=False)

    def cmd(self, cmd: str):
        with self.lock:
            if cmd == "p":
                self.log.print()
            else:
                self.log.add(cmd, self.current_term)
