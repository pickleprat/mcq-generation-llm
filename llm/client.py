from typing import Any, Iterable
from llm.gemini.geminiclient import GeminiClient
from llm.openai.openaiclient import OpenAIClient


class LLMClient:
    def __init__(
        self,
        client: str = "gemini",
        api_key: str | None = None,
        **kwargs: Any,
    ):
        client = client.lower()

        if client == "gemini":
            self._client = GeminiClient(api_key=api_key, **kwargs)
        elif client == "openai":
            self._client = OpenAIClient(api_key=api_key, **kwargs)
        else:
            raise ValueError(f"Unsupported client: {client}")

    # -------- Capability passthroughs -------- #

    @property
    def supports_batch(self) -> bool:
        return self._client.supports_batch

    @property
    def supports_streaming(self) -> bool:
        return self._client.supports_streaming

    @property
    def supports_pdfs(self) -> bool:
        return self._client.supports_pdfs

    # -------- Core API -------- #

    def generate(self, prompt: str, **kwargs: Any) -> str:
        return self._client.generate(prompt, **kwargs)

    def generate_batch(self, prompts: list[str], **kwargs: Any) -> list[str]:
        return self._client.generate_batch(prompts, **kwargs)

    def stream(self, prompt: str, **kwargs: Any) -> Iterable[str]:
        return self._client.stream(prompt, **kwargs)

    # -------- PDF API -------- #

    def generate_with_pdfs(
        self,
        prompt: str,
        pdfs: list[bytes],
        **kwargs: Any,
    ) -> str:
        return self._client.generate_with_pdfs(prompt, pdfs, **kwargs)

    def stream_with_pdfs(
        self,
        prompt: str,
        pdfs: list[bytes],
        **kwargs: Any,
    ) -> Iterable[str]:
        return self._client.stream_with_pdfs(prompt, pdfs, **kwargs)

    # -------- Config -------- #

    def set_params(self, **params: Any) -> None:
        self._client.set_params(**params)