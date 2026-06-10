from abc import ABC, abstractmethod


class Tool(ABC):
    name = ""
    description = ""
    scope = []

    @abstractmethod
    def run(self, params: dict) -> dict:
        ...
