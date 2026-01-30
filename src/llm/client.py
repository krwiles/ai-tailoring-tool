from abc import ABC, abstractmethod


class LLMClient(ABC):
    """Abstract LLM engine for prompting"""

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Return the model's response from the input prompt"""
        pass
