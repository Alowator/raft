from dataclasses import dataclass

@dataclass
class GetVoteRequest:
    node: str
    term: int
    last_log_index: int
    last_log_term: int

@dataclass
class AppendEntriesRequest:
    pass
