import types
from pathlib import Path
from typing import List

import pytest
from docx import Document

from src.io import FileManager


@pytest.fixture
def fake_settings(tmp_path):
    """A minimal settings stand-in for FileManager tests, decoupled from ini parsing."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    return types.SimpleNamespace(
        project_dir=tmp_path,
        output_dir=output_dir,
        resume_name="resume_out.docx",
        cover_letter_name="cover_letter_out.docx",
    )


@pytest.fixture
def file_manager(fake_settings):
    return FileManager(fake_settings)


@pytest.fixture
def make_docx(tmp_path):
    """Write a .docx with the given paragraphs under tmp_path and return its project-relative path."""

    def _make(relative_path: str, paragraphs: List[str]) -> Path:
        full_path = tmp_path / relative_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        doc = Document()
        for text in paragraphs:
            doc.add_paragraph(text)
        doc.save(full_path)
        return Path(relative_path)

    return _make
