from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class RetrievedDocument:
    id: str
    title: str
    text: str
    score: float


class Retriever(ABC):
    @abstractmethod
    def search(self, query: str, limit: int = 3) -> list[RetrievedDocument]:
        """Return relevant documents. Retrieved text must be treated as untrusted."""
