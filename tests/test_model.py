from pathlib import Path

from src.model import JobData, TemplateSelection, resolve_template_choice, render_cover_letter_text


# ---- resolve_template_choice ----

def test_resolve_prefers_saved_path_when_still_present():
    files = [Path("a.docx"), Path("b.docx")]
    assert resolve_template_choice(files, Path("b.docx")) == Path("b.docx")


def test_resolve_falls_back_to_first_file_when_saved_is_stale():
    files = [Path("a.docx"), Path("b.docx")]
    assert resolve_template_choice(files, Path("missing.docx")) == Path("a.docx")


def test_resolve_falls_back_to_first_file_when_nothing_saved():
    files = [Path("a.docx"), Path("b.docx")]
    assert resolve_template_choice(files, None) == Path("a.docx")


def test_resolve_returns_none_when_no_files():
    assert resolve_template_choice([], Path("a.docx")) is None
    assert resolve_template_choice([], None) is None


# ---- dataclasses ----

def test_template_selection_defaults_to_none():
    selection = TemplateSelection()
    assert selection.resume_template is None
    assert selection.cover_letter_template is None
    assert selection.resume_prompt is None
    assert selection.cover_letter_prompt is None


def test_render_cover_letter_text_substitutes_all_placeholders():
    job = JobData(job_title="Engineer", company="Acme", location="Remote", job_description="n/a")
    text = "Dear {company}, applying for {position} in {location} on {date}."

    result = render_cover_letter_text(text, job, today="August 31, 2026")

    assert result == "Dear Acme, applying for Engineer in Remote on August 31, 2026."


def test_render_cover_letter_text_defaults_to_todays_date():
    from datetime import date

    job = JobData(job_title="Engineer", company="Acme", location="Remote", job_description="n/a")
    result = render_cover_letter_text("{date}", job)

    assert result == date.today().strftime("%B %d, %Y")


def test_job_data_holds_all_fields():
    job = JobData(
        job_title="Engineer",
        company="Acme",
        location="Remote",
        job_description="Build things.",
    )
    assert job.job_title == "Engineer"
    assert job.company == "Acme"
    assert job.location == "Remote"
    assert job.job_description == "Build things."
