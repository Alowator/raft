import logging

class Entry:
    def __init__(self, index: int, term: int, value: str):
        self._index = index
        self._term = term
        self._value = value

    def get_index(self) -> int:
        return self._index

    def get_term(self) -> int:
        return self._index

    def get_value(self) -> str:
        return self._value

    def __str__(self):
        return self._value

class Log:
    def __init__(self, init_term: int):
        self._log = [Entry(0, init_term, "")]

    def get_entry(self, index: int) -> Entry:
        return self._log[index]

    def get_last_log_index(self) -> int:
        return self._log[-1].get_index()

    def get_last_log_term(self):
        return self._log[-1].get_term()

    def contains(self, index: int) -> bool:
        return 0 <= index < len(self._log)

    def add(self, value: str, term: int):
        self._log.append(Entry(self.get_last_log_index() + 1, term, value))

    def truncate_from(self, index: int):
        self._log = self._log[0:index]

    def print(self):
        res = ["Log contains:"]
        for entry in self._log:
            res.append(str(entry))
        logging.info("\n".join(res))
