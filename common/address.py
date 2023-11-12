from dataclasses import dataclass
from typing import Tuple


@dataclass
class Address:
    ip: str
    port: int

    def __str__(self):
        return self.ip + ":" + str(self.port)

    def tuple(self) -> Tuple[str, int]:
        return (self.ip, self.port)

    def get_http_url(self) -> str:
        return f"http://{self}/"
