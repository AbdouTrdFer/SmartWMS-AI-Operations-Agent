from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class LLMContext:
    message: str
    facts: list[str]
    retrieved_notes: list[str]
    structured_results: list[dict[str, Any]]


class LLMProvider(ABC):
    @abstractmethod
    def generate(self, context: LLMContext) -> str:
        """Generate an answer from trusted tool facts and untrusted retrieved notes."""
