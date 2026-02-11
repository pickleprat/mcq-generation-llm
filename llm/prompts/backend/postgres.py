from llm.prompts.backend.interface import PromptBackend 

class PostgresPromptBackend(PromptBackend):
    def __init__(self, db_session):
        self.db_session = db_session

    def get(self, name: str, user_id: str | None = None) -> str:
        # 1. Check user override
        # 2. Fallback to system default
        pass