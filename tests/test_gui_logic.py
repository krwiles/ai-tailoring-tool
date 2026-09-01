from pathlib import Path

from src.io.gui_logic import validate_job_fields, resolve_template_selection
from src.model import TemplateSelection


# ---- validate_job_fields ----

def test_validate_job_fields_all_present_returns_no_errors():
    assert validate_job_fields("Acme", "Engineer", "Some description") == {}


def test_validate_job_fields_reports_each_missing_field():
    errors = validate_job_fields("", "", "")
    assert errors == {
        "company": "Company Required",
        "position": "Position Required",
        "description": "Required",
    }


def test_validate_job_fields_reports_only_missing_fields():
    errors = validate_job_fields("Acme", "", "Some description")
    assert errors == {"position": "Position Required"}


# ---- resolve_template_selection ----

def test_resolve_template_selection_reports_resolved_and_missing_categories(file_manager, tmp_path):
    (tmp_path / "resumes").mkdir()
    (tmp_path / "resumes" / "a.docx").write_text("x")
    # "cover_letters" folder is intentionally left missing/empty.

    categories = (
        ("resume_template", Path("resumes"), "*.docx", "Resume Template"),
        ("cover_letter_template", Path("cover_letters"), "*.docx", "Cover Letter Template"),
    )
    saved = TemplateSelection()

    result = resolve_template_selection(file_manager, categories, saved)

    assert result.selection.resume_template == Path("resumes", "a.docx")
    assert result.selection.cover_letter_template is None
    assert result.name_maps["resume_template"] == {"a.docx": Path("resumes", "a.docx")}
    assert result.name_maps["cover_letter_template"] == {}
    assert result.missing_labels == ["Cover Letter Template"]


def test_resolve_template_selection_keeps_saved_choice_when_still_valid(file_manager, tmp_path):
    (tmp_path / "resumes").mkdir()
    (tmp_path / "resumes" / "a.docx").write_text("x")
    (tmp_path / "resumes" / "b.docx").write_text("x")

    categories = (("resume_template", Path("resumes"), "*.docx", "Resume Template"),)
    saved = TemplateSelection(resume_template=Path("resumes", "b.docx"))

    result = resolve_template_selection(file_manager, categories, saved)

    assert result.selection.resume_template == Path("resumes", "b.docx")
    assert result.missing_labels == []
