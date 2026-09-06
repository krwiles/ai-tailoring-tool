import sys

import pytest

from src.config.settings import AppSettings, TEMPLATE_KEYS
from src.model import TemplateSelection


@pytest.fixture
def frozen_in(tmp_path, monkeypatch):
    """Point AppSettings.project_dir at tmp_path via the app's own 'packaged exe' code path."""
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "executable", str(tmp_path / "fake.exe"))
    return tmp_path


def test_creates_default_ini_when_missing(frozen_in):
    settings = AppSettings()

    ini_path = frozen_in / "settings.ini"
    assert ini_path.exists()
    assert settings.config.has_section("llm")
    assert settings.config.has_section("paths")
    assert settings.config.has_section("files")
    assert settings.config.has_section("templates")
    for key in TEMPLATE_KEYS:
        assert settings.config.has_option("templates", key)
        assert settings.config["templates"][key] == ""


def test_backfills_missing_templates_section_without_touching_other_values(frozen_in):
    output_dir = frozen_in / "out"
    (frozen_in / "settings.ini").write_text(
        "[llm]\n"
        "model = custom-model\n\n"
        "[paths]\n"
        f"output_dir = {output_dir.as_posix()}\n\n"
        "[files]\n"
        "cover_letter_out = cl.docx\n"
        "resume_out = r.docx\n"
    )

    settings = AppSettings()

    assert settings.model == "custom-model"
    assert settings.output_dir == output_dir.resolve()
    assert settings.cover_letter_name == "cl.docx"
    assert settings.resume_name == "r.docx"

    assert settings.config.has_section("templates")
    for key in TEMPLATE_KEYS:
        assert settings.config["templates"][key] == ""

    # Backfill was persisted to disk, not just held in memory.
    reread = AppSettings()
    assert reread.config.has_section("templates")


def test_backfill_is_a_noop_once_templates_section_is_complete(frozen_in):
    (frozen_in / "settings.ini").write_text(
        "[llm]\nmodel = m\n\n"
        "[paths]\noutput_dir = .\n\n"
        "[files]\ncover_letter_out = cl.docx\nresume_out = r.docx\n\n"
        "[templates]\n"
        "resume_template = a.docx\n"
        "cover_letter_template = b.docx\n"
        "resume_prompt = c.txt\n"
        "cover_letter_prompt = d.txt\n"
    )

    settings = AppSettings()

    assert settings._backfill_templates_section() is False


def test_template_selection_round_trips_through_settings(frozen_in):
    settings = AppSettings()
    from pathlib import Path

    selection = TemplateSelection(
        resume_template=Path("data", "resumes", "a.docx"),
        cover_letter_template=Path("data", "cover_letters", "b.docx"),
        resume_prompt=Path("prompts", "resume", "c.txt"),
        cover_letter_prompt=None,
    )

    settings.save_template_selection(selection)
    loaded = settings.load_template_selection()

    assert loaded == selection
