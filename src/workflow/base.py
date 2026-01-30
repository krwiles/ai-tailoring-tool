from abc import ABC, abstractmethod
from pathlib import Path

from src.config import AppSettings
from src.io import FileManager
from src.llm import LLMClient
from src.model import JobData
from src.prompt import PromptBuilder


class BaseWorkflow(ABC):

    def __init__(self,
                 prompt_builder: PromptBuilder,
                 llm_client: LLMClient,
                 file_manager: FileManager,
                 settings: AppSettings
                 ):

        self.prompt_builder = prompt_builder
        self.llm_client = llm_client
        self.file_manager = file_manager
        self.settings = settings

    def run(self, job_data: JobData):
        prompt = self.prompt_builder.build(job_data)
        output = self.llm_client.generate(prompt)

        directory = Path(
            self.file_manager.sanitize_dirname(job_data.company),
            self.file_manager.sanitize_dirname(job_data.job_title)
        )

        self.copy_template(directory, job_data)
        self.write_output(directory, output)

    @abstractmethod
    def copy_template(self, directory: Path, job_data: JobData):
        pass

    @abstractmethod
    def write_output(self, directory: Path, output: str):
        pass
