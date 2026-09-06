from pathlib import Path

from src.model import JobData, TemplateSelection
from src.workflow.base import BaseWorkflow


class CoverLetterWorkflow(BaseWorkflow):

    def copy_template(self, directory: Path, job_data: JobData, template_selection: TemplateSelection):
        self.file_manager.copy_cover_letter(directory, job_data, template_selection.cover_letter_template)

    def write_output(self, directory: Path, output: str):
        self.file_manager.write_docx(output, directory / "tailored_cover_letter.docx")
