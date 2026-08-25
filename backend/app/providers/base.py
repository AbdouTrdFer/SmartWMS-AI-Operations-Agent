from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class LLMContext:
    message: str
    facts: list[str]
    retrieved_notes: list[str]


class LLMProvider(ABC):
    @abstractmethod
    def generate(self, context: LLMContext) -> str:
        """Generate an answer from trusted tool facts and untrusted retrieved notes."""
