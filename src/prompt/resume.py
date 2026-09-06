from src.model import JobData, TemplateSelection
from src.prompt import PromptBuilder


class ResumePromptBuilder(PromptBuilder):

    def build(self, job_data: JobData, template_selection: TemplateSelection) -> str:
        resume = self.file_manager.read_docx(template_selection.resume_template)
        prompt = self.file_manager.load_text(template_selection.resume_prompt)
        prompt = prompt.format(
            resume=resume,
            job_description=job_data.job_description
        )

        return prompt
