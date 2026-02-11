from llm.interface.aiclient import AIClient
from typing import Any, Iterable
from google import genai
from google.genai import types


class GeminiClient(AIClient):
    supports_batch = True
    supports_streaming = True
    supports_pdfs = True

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "gemini-2.5-flash-lite",
        **generation_params: Any,
    ):
        super().__init__(api_key)

        self.client = genai.Client(api_key=api_key) if api_key else genai.Client()
        self.model = model
        self.generation_params = generation_params

    def set_params(self, **params: Any) -> None:
        self.generation_params.update(params)

    def generate(self, prompt: str, **kwargs: Any) -> str:
        params = {**self.generation_params, **kwargs}

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            **params,
        )
        return response.text

    def generate_batch(self, prompts: list[str], **kwargs: Any) -> list[str]:
        params = {**self.generation_params, **kwargs}
        outputs: list[str] = []

        for prompt in prompts:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                **params,
            )
            outputs.append(response.text)

        return outputs

    def stream(self, prompt: str, **kwargs: Any) -> Iterable[str]:
        params = {**self.generation_params, **kwargs}

        stream = self.client.models.generate_content_stream(
            model=self.model,
            contents=prompt,
            **params,
        )

        for chunk in stream:
            if chunk.text:
                yield chunk.text

    def generate_with_pdfs(
        self,
        prompt: str,
        pdfs: list[bytes],
        **kwargs: Any,
    ) -> str:
        params = {**self.generation_params, **kwargs}

        parts = [types.Part.from_text(text=prompt)]

        for pdf in pdfs:
            parts.append(
                types.Part.from_bytes(
                    data=pdf,
                    mime_type="application/pdf",
                )
            )

        response = self.client.models.generate_content(
            model=self.model,
            contents=parts,
            **params,
        )

        return response.text

    def stream_with_pdfs(
        self,
        prompt: str,
        pdfs: list[bytes],
        **kwargs: Any,
    ):

        params = {**self.generation_params, **kwargs}

        parts = [types.Part.from_text(text=prompt)]

        for pdf in pdfs:
            parts.append(
                types.Part.from_bytes(
                    data=pdf,
                    mime_type="application/pdf",
                )
            )

        stream = self.client.models.generate_content_stream(
            model=self.model,
            contents=parts,
            **params,
        )

        for chunk in stream:
            if chunk.text:
                yield chunk.text