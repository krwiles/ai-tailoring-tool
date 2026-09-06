from src.model import JobData, TemplateSelection, render_cover_letter_text
from src.prompt import PromptBuilder


class CoverLetterPromptBuilder(PromptBuilder):

    def build(self, job_data: JobData, template_selection: TemplateSelection) -> str:
        cover_letter = self.file_manager.read_docx(template_selection.cover_letter_template)
        cover_letter = render_cover_letter_text(cover_letter, job_data)

        prompt = self.file_manager.load_text(template_selection.cover_letter_prompt)
        prompt = prompt.format(
            cover_letter=cover_letter,
            job_description=job_data.job_description
        )

        return prompt
