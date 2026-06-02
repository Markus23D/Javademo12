from abc import ABC, abstractmethod

class Skill(ABC):

    @abstractmethod
    def can_handle(self, text: str) -> float:
        pass

    @abstractmethod
    def handle(self, text: str, context):
        pass