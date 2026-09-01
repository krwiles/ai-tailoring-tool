from pathlib import Path
from unittest.mock import Mock

from src.model import JobData, TemplateSelection
from src.workflow import ResumeWorkflow, CoverLetterWorkflow


def _passthrough_file_manager():
    mock_fm = Mock()
    mock_fm.sanitize_dirname.side_effect = lambda name: name
    return mock_fm


def test_resume_workflow_run_orchestrates_prompt_llm_copy_and_write():
    mock_pb = Mock()
    mock_pb.build.return_value = "PROMPT"
    mock_llm = Mock()
    mock_llm.generate.return_value = "OUTPUT"
    mock_fm = _passthrough_file_manager()

    job = JobData(job_title="Engineer", company="Acme", location="Remote", job_description="Do stuff")
    selection = TemplateSelection(resume_template=Path("data", "resumes", "x.docx"))

    workflow = ResumeWorkflow(prompt_builder=mock_pb, llm_client=mock_llm, file_manager=mock_fm, settings=Mock())
    workflow.run(job, selection)

    mock_pb.build.assert_called_once_with(job, selection)
    mock_llm.generate.assert_called_once_with("PROMPT")

    directory = Path("Acme", "Engineer")
    mock_fm.copy_resume.assert_called_once_with(directory, selection.resume_template)
    mock_fm.write_docx.assert_called_once_with("OUTPUT", directory / "tailored_resume.docx")


def test_cover_letter_workflow_run_orchestrates_prompt_llm_copy_and_write():
    mock_pb = Mock()
    mock_pb.build.return_value = "PROMPT"
    mock_llm = Mock()
    mock_llm.generate.return_value = "OUTPUT"
    mock_fm = _passthrough_file_manager()

    job = JobData(job_title="Engineer", company="Acme", location="Remote", job_description="Do stuff")
    selection = TemplateSelection(cover_letter_template=Path("data", "cover_letters", "x.docx"))

    workflow = CoverLetterWorkflow(prompt_builder=mock_pb, llm_client=mock_llm, file_manager=mock_fm, settings=Mock())
    workflow.run(job, selection)

    mock_pb.build.assert_called_once_with(job, selection)
    mock_llm.generate.assert_called_once_with("PROMPT")

    directory = Path("Acme", "Engineer")
    mock_fm.copy_cover_letter.assert_called_once_with(directory, job, selection.cover_letter_template)
    mock_fm.write_docx.assert_called_once_with("OUTPUT", directory / "tailored_cover_letter.docx")


def test_run_sanitizes_company_and_title_into_the_output_directory():
    mock_pb = Mock()
    mock_pb.build.return_value = "PROMPT"
    mock_llm = Mock()
    mock_llm.generate.return_value = "OUTPUT"
    mock_fm = Mock()
    mock_fm.sanitize_dirname.side_effect = lambda name: name.replace("/", "_")

    job = JobData(job_title="Role/With/Slashes", company="Acme/Inc", location="", job_description="")
    selection = TemplateSelection()

    workflow = ResumeWorkflow(prompt_builder=mock_pb, llm_client=mock_llm, file_manager=mock_fm, settings=Mock())
    workflow.run(job, selection)

    mock_fm.sanitize_dirname.assert_any_call("Acme/Inc")
    mock_fm.sanitize_dirname.assert_any_call("Role/With/Slashes")
    mock_fm.copy_resume.assert_called_once_with(Path("Acme_Inc", "Role_With_Slashes"), None)
