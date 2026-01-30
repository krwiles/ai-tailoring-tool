from pathlib import Path

from src.model import JobData
from src.workflow.base import BaseWorkflow


class CoverLetterWorkflow(BaseWorkflow):

    def copy_template(self, directory: Path, job_data: JobData):
        self.file_manager.copy_cover_letter(directory, job_data)

    def write_output(self, directory: Path, output: str):
        self.file_manager.write_docx(output, directory / "tailored_cover_letter.docx")
