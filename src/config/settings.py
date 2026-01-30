from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppSettings:
    model: str = "gpt-5-mini"
    project_dir: Path = Path(__file__).resolve().parents[2]
    output_dir: Path = Path(r"C:\Users\assas\OneDrive\Career")
    cover_letter_name: str = "Kurtis_Wiles_cover_letter.docx"
    resume_name: str = "Kurtis_Wiles_resume.docx"
