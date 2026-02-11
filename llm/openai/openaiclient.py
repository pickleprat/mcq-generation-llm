
from typing import Any
from llm.interface.aiclient import AIClient

class OpenAIClient(AIClient):
    def __init__(self, api_key: str, **params: Any):
        super().__init__(api_key)
        self.params = params

    def set_params(self, **params: Any) -> None:
        self.params.update(params)

    def generate(self, prompt: str, **kwargs: Any) -> str:
        raise NotImplementedError("OpenAIClient not implemented yet")