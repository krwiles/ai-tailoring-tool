import configparser
import sys
from pathlib import Path
from typing import Optional

from src.model import TemplateSelection

DEFAULT_INI = """\
[llm]
model = gpt-5-mini

[paths]
output_dir = .

[files]
cover_letter_out = Template_cover_letter.docx
resume_out = Template_resume.docx

[templates]
resume_template =
cover_letter_template =
resume_prompt =
cover_letter_prompt =
"""

TEMPLATE_KEYS = (
    "resume_template",
    "cover_letter_template",
    "resume_prompt",
    "cover_letter_prompt",
)


class AppSettings:
    def __init__(self):
        # Determine the base project directory
        if getattr(sys, 'frozen', False):
            # Running as PyInstaller exe
            self.project_dir = Path(sys.executable).parent.resolve()
        else:
            # Running as script
            self.project_dir = Path(__file__).resolve().parents[2]

        self.config_path = self.project_dir.joinpath("settings.ini").resolve()

        if not self.config_path.exists():
            self._create_default()

        self.config = configparser.ConfigParser()
        self.config.read(self.config_path)

        self.model = self.config["llm"]["model"]
        self.output_dir = Path(self.config["paths"]["output_dir"]).resolve()
        self.cover_letter_name = self.config["files"]["cover_letter_out"]
        self.resume_name = self.config["files"]["resume_out"]

        # Backfill [templates] for settings.ini files that predate this feature.
        if self._backfill_templates_section():
            self._write_config()

    def _create_default(self):
        print("No settings.ini found. Creating default.")
        self.config_path.write_text(DEFAULT_INI)

    def _backfill_templates_section(self) -> bool:
        """Ensure [templates] and all its keys exist. Returns True if changed."""
        changed = False
        if not self.config.has_section("templates"):
            self.config.add_section("templates")
            changed = True
        for key in TEMPLATE_KEYS:
            if not self.config.has_option("templates", key):
                self.config.set("templates", key, "")
                changed = True
        return changed

    def _write_config(self) -> None:
        with self.config_path.open("w", encoding="utf-8") as f:
            self.config.write(f)

    def load_template_selection(self) -> TemplateSelection:
        """Read the persisted template/prompt selection from settings.ini."""

        def get_path(key: str) -> Optional[Path]:
            value = self.config["templates"].get(key, "").strip()
            return Path(value) if value else None

        return TemplateSelection(
            resume_template=get_path("resume_template"),
            cover_letter_template=get_path("cover_letter_template"),
            resume_prompt=get_path("resume_prompt"),
            cover_letter_prompt=get_path("cover_letter_prompt"),
        )

    def save_template_selection(self, selection: TemplateSelection) -> None:
        """Persist the given template/prompt selection to settings.ini."""

        def to_str(p: Optional[Path]) -> str:
            return p.as_posix() if p else ""

        self.config["templates"]["resume_template"] = to_str(selection.resume_template)
        self.config["templates"]["cover_letter_template"] = to_str(selection.cover_letter_template)
        self.config["templates"]["resume_prompt"] = to_str(selection.resume_prompt)
        self.config["templates"]["cover_letter_prompt"] = to_str(selection.cover_letter_prompt)
        self._write_config()
