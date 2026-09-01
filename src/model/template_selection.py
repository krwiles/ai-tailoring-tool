from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


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


def resolve_template_choice(files: List[Path], saved_path: Optional[Path]) -> Optional[Path]:
    """Pick which file a category should use, given what's on disk and the saved preference.

    Prefers saved_path if it's still among files; otherwise falls back to the first
    file (files is expected to already be sorted); otherwise None if there's nothing
    to choose from.
    """
    if saved_path in files:
        return saved_path
    return files[0] if files else None
