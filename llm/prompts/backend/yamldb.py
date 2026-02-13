from pathlib import Path
from llm.prompts.backend.interface import PromptBackend 
import yaml 
import os 

class YamlPromptBackend(PromptBackend):
    def __init__(self, prompt_dir: str = os.path.join(os.getcwd(), "llm", "prompts", "db")):
        self.prompt_dir = Path(prompt_dir)

    def get(self, name: str, user_id: str | None = None) -> str:
        file_path = self.prompt_dir / f"{name}.yml"

        if not file_path.exists():
            raise FileNotFoundError(f"Prompt '{name}' not found")

        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        return data["template"]