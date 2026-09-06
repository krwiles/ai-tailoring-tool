from datetime import date
from typing import Optional

from src.model.job_data import JobData


def render_cover_letter_text(text: str, job_data: JobData, today: Optional[str] = None) -> str:
    """Substitute the {date}/{location}/{company}/{position} placeholders in cover
    letter text with today's date and the given job data. The single source of truth
    for the cover letter placeholder contract — used both when copying the raw
    template (FileManager.copy_cover_letter) and when building the tailoring prompt
    (CoverLetterPromptBuilder.build).
    """
    if today is None:
        today = date.today().strftime("%B %d, %Y")

    return text.format(
        date=today,
        location=job_data.location,
        company=job_data.company,
        position=job_data.job_title,
    )
