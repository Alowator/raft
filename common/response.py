from dataclasses import dataclass

@dataclass
class GetVoteResponse:
    term: int
    vote_granted: bool

@dataclass
class AppendEntriesResponse:
    node: str
    term: int
    success: bool
    last_index: int

@dataclass
class SetResponse:
    success: bool
    redirect_to: str | None
