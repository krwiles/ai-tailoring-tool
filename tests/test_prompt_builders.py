from pathlib import Path
from unittest.mock import Mock

import pytest

from src.model import JobData, TemplateSelection
from src.prompt import PromptBuilder, ResumePromptBuilder, CoverLetterPromptBuilder


def test_prompt_builder_is_abstract():
    with pytest.raises(TypeError):
        PromptBuilder(Mock())


def test_resume_prompt_builder_reads_selected_files_and_formats_prompt():
    mock_fm = Mock()
    mock_fm.read_docx.return_value = "RESUME TEXT"
    mock_fm.load_text.return_value = "PROMPT: {resume} | job: {job_description}"

    selection = TemplateSelection(
        resume_template=Path("data", "resumes", "x.docx"),
        resume_prompt=Path("prompts", "resume", "y.txt"),
    )
    job = JobData(job_title="Engineer", company="Acme", location="Remote", job_description="Do stuff")

    result = ResumePromptBuilder(mock_fm).build(job, selection)

    mock_fm.read_docx.assert_called_once_with(selection.resume_template)
    mock_fm.load_text.assert_called_once_with(selection.resume_prompt)
    assert result == "PROMPT: RESUME TEXT | job: Do stuff"


def test_cover_letter_prompt_builder_reads_selected_files_and_formats_prompt():
    from datetime import date

    mock_fm = Mock()
    mock_fm.read_docx.return_value = "Dear {company}, applying for {position} in {location} on {date}."
    mock_fm.load_text.return_value = "PROMPT: {cover_letter} | job: {job_description}"

    selection = TemplateSelection(
        cover_letter_template=Path("data", "cover_letters", "x.docx"),
        cover_letter_prompt=Path("prompts", "cover_letter", "y.txt"),
    )
    job = JobData(job_title="Engineer", company="Acme", location="Remote", job_description="Do stuff")

    result = CoverLetterPromptBuilder(mock_fm).build(job, selection)

    mock_fm.read_docx.assert_called_once_with(selection.cover_letter_template)
    mock_fm.load_text.assert_called_once_with(selection.cover_letter_prompt)

    today = date.today().strftime("%B %d, %Y")
    expected_letter = f"Dear Acme, applying for Engineer in Remote on {today}."
    assert result == f"PROMPT: {expected_letter} | job: Do stuff"
