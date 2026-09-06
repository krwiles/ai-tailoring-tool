"""Pure, GUI-free logic used by AppGUI — testable without constructing Tkinter widgets.

Extracted so the rules that decide what's valid and which template files get used
have their own seam, separate from widget construction and mutation.
"""
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

from src.io.file_manager import FileManager
from src.model import TemplateSelection, resolve_template_choice

# (TemplateSelection field name, folder relative to project_dir, glob pattern, display label)
TemplateCategory = Tuple[str, Path, str, str]


def validate_job_fields(company: str, position: str, description: str) -> Dict[str, str]:
    """Return a field-name -> error-message mapping for any missing required fields."""
    errors = {}
    if not company:
        errors["company"] = "Company Required"
    if not position:
        errors["position"] = "Position Required"
    if not description:
        errors["description"] = "Required"
    return errors


@dataclass
class TemplateSelectionResolution:
    selection: TemplateSelection
    name_maps: Dict[str, Dict[str, Path]]
    missing_labels: List[str]


def resolve_template_selection(
    file_manager: FileManager,
    categories: Tuple[TemplateCategory, ...],
    saved: TemplateSelection,
) -> TemplateSelectionResolution:
    """Scan each category's folder, resolve saved-vs-fallback-vs-none, and report gaps."""
    resolved_fields = {}
    name_maps: Dict[str, Dict[str, Path]] = {}
    missing_labels: List[str] = []

    for field_name, folder, pattern, label in categories:
        files = file_manager.list_files(folder, pattern)
        saved_path = getattr(saved, field_name)
        selected = resolve_template_choice(files, saved_path)

        name_maps[field_name] = {f.name: f for f in files}
        resolved_fields[field_name] = selected
        if selected is None:
            missing_labels.append(label)

    return TemplateSelectionResolution(
        selection=TemplateSelection(**resolved_fields),
        name_maps=name_maps,
        missing_labels=missing_labels,
    )
