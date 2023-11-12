from enum import Enum, auto

class State(Enum):
    FOLLOWER = auto()
    CANDIDATE = auto()
    LEADER = auto()
