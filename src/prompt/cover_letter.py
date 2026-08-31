from datetime import date

from src.model import JobData, TemplateSelection
from src.prompt import PromptBuilder


class CoverLetterPromptBuilder(PromptBuilder):

    def build(self, job_data: JobData, template_selection: TemplateSelection) -> str:
        today = date.today().strftime("%B %d, %Y")

        cover_letter = self.file_manager.read_docx(template_selection.cover_letter_template)
        cover_letter = cover_letter.format(
            date=today,
            location=job_data.location,
            company=job_data.company,
            position=job_data.job_title
        )

        prompt = self.file_manager.load_text(template_selection.cover_letter_prompt)
        prompt = prompt.format(
            cover_letter=cover_letter,
            job_description=job_data.job_description
        )

        return prompt
