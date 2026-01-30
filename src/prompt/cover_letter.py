from datetime import date
from pathlib import Path

from src.model import JobData
from src.prompt import PromptBuilder


class CoverLetterPromptBuilder(PromptBuilder):

    def build(self, job_data: JobData) -> str:
        today = date.today().strftime("%B %d, %Y")

        cover_letter = self.file_manager.read_docx(Path("data", "cover_letter.docx"))
        cover_letter = cover_letter.format(
            date=today,
            location=job_data.location,
            company=job_data.company,
            position=job_data.job_title
        )

        prompt = self.file_manager.load_text(Path("prompts", "cover_letter_prompt.txt"))
        prompt = prompt.format(
            cover_letter=cover_letter,
            job_description=job_data.job_description
        )

        return prompt
