class Hashtable:
    def __init__(self):
        self._table = {}

    def set(self, key, value):
        self._table[key] = value

    def get(self, key):
        return self._table.get(key)

