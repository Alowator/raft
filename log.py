class Log():
    def __init__(self, init_term: int):
        self._log = [Entry(0, init_term)]

    def get_last_log_index(self) -> int:
        return self._log[-1].get_index()

    def get_last_log_term(self):
        return self._log[-1].get_term()

class Entry:
    def __init__(self, index: int, term: int):
        self._index = index
        self._term = term

    def get_index(self) -> int:
        return self._index

    def get_term(self) -> int:
        return self._index
