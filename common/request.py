from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class GetVoteRequest:
    node: str
    term: int
    last_log_index: int
    last_log_term: int

@dataclass
class AppendEntriesRequest:
    node: str
    term: int
    prev_log_index: int
    prev_log_term: int
    entries: List[Tuple[int, str]]
    leader_commit: int
