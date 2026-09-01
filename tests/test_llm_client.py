import types

import pytest

from src.llm import LLMClient, OpenAIClient


def test_llm_client_is_abstract():
    with pytest.raises(TypeError):
        LLMClient()


def test_openai_client_generate_returns_output_text(mocker):
    mock_openai_cls = mocker.patch("src.llm.openai_client.OpenAI")
    mock_client_instance = mock_openai_cls.return_value
    mock_client_instance.responses.create.return_value = mocker.Mock(output_text="GENERATED TEXT")

    settings = types.SimpleNamespace(model="gpt-test")
    client = OpenAIClient(settings)

    result = client.generate("some prompt")

    assert result == "GENERATED TEXT"
    mock_client_instance.responses.create.assert_called_once_with(model="gpt-test", input="some prompt")
