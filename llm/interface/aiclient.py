from abc import ABC, abstractmethod
from typing import Any, Iterable, List

class AIClient(ABC):
    supports_batch: bool = False
    supports_streaming: bool = False
    supports_pdfs: bool = False

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key

    @abstractmethod
    def generate(self, prompt: str, **kwargs: Any) -> str:
        pass

    def generate_batch(self, prompts: List[str], **kwargs: Any) -> List[str]:
        raise NotImplementedError("Batch generation not supported")

    def stream(self, prompt: str, **kwargs: Any) -> Iterable[str]:
        raise NotImplementedError("Streaming not supported")

    def generate_with_pdfs(
        self,
        prompt: str,
        pdfs: List[bytes],
        **kwargs: Any,
    ) -> str:
        raise NotImplementedError("PDF input not supported")

    @abstractmethod
    def set_params(self, **params: Any) -> None:
        pass