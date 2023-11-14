from dataclasses import dataclass

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
    entry: str | None
    leader_commit: int
