from dataclasses import dataclass, asdict

@dataclass
class GetVoteResponse:
    term: int
    vote_granted: bool

    dict = asdict

@dataclass
class AppendEntriesResponse:
    node: str
    term: int
    success: bool

    dict = asdict
