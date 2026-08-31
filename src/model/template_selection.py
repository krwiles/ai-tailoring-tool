from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class TemplateSelection:
    """The user's current choice of resume/cover-letter template and prompt files.

    Each field is a project-relative Path (same convention as FileManager's other
    methods), or None if that category has no matching file on disk. This is a
    standing user preference persisted in settings.ini, not per-job data — kept
    separate from JobData for that reason.
    """
    resume_template: Optional[Path] = None
    cover_letter_template: Optional[Path] = None
    resume_prompt: Optional[Path] = None
    cover_letter_prompt: Optional[Path] = None
