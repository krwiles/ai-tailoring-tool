from abc import ABC, abstractmethod

from src.io import FileManager


class PromptBuilder(ABC):

    def __init__(self, file_manager: FileManager):
        self.file_manager = file_manager

    @abstractmethod
    def build(self, job_data):
        """Return full prompt string for LLM"""
        pass