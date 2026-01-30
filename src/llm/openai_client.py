from openai import OpenAI

from src.llm import LLMClient


class OpenAIClient(LLMClient):

    def __init__(self, settings):
        self.model = settings.model
        self.client = OpenAI()

    def generate(self, prompt: str) -> str:
        response = self.client.responses.create(
            model=self.model,
            input=prompt
        )
        return response.output_text
