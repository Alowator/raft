from dataclasses import dataclass
from typing import Tuple

@dataclass
class Address:
    ip: str
    port: str

    def __str__(self):
        return self.ip + ":" + self.port

    def __eq__(self, other):
        return self.ip == other.ip and self.port == other.port

    def tuple(self) -> Tuple[str, int]:
        return (self.ip, int(self.port))

    def get_http_url(self) -> str:
        return f"http://{self}/"
