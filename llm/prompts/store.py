from llm.prompts.backend.interface import PromptBackend
from llm.prompts.backend.yamldb import YamlPromptBackend
from llm.prompts.handler import PromptHandle

class PromptStore:
    _backend: PromptBackend = YamlPromptBackend()

    topic_extraction = PromptHandle("topic_extraction", _backend)
    mcq_generation = PromptHandle("mcq_generation", _backend)