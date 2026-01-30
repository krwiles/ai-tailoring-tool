from pathlib import Path

from src.model import JobData
from src.prompt import PromptBuilder


class ResumePromptBuilder(PromptBuilder):

    def build(self, job_data: JobData) -> str:
        resume = self.file_manager.read_docx(Path("data", "resume.docx"))
        prompt = self.file_manager.load_text(Path("prompts", "resume_prompt.txt"))
        prompt = prompt.format(
            resume=resume,
            job_description=job_data.job_description
        )

        return prompt
