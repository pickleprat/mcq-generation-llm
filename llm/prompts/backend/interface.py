from abc import ABC, abstractmethod

class PromptBackend(ABC):
    @abstractmethod
    def get(self, name: str, user_id: str | None = None) -> str:
        """
        Retrieve the prompt template.

        Resolution order (future):
        1. User-specific override
        2. Org-level override
        3. System default
        """
        pass