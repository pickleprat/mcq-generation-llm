from llm.prompts.backend.interface import PromptBackend

class PromptHandle:
    def __init__(self, name: str, backend: PromptBackend):
        self.name = name
        self.backend = backend

    def get(self, user_id: str | None = None) -> str:
        return self.backend.get(self.name, user_id=user_id)