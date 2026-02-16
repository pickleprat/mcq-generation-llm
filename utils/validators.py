from pydantic import ValidationError
from schema.mcq import MCQList

def validate_mcqs(data):
    try:
        validated = MCQList.model_validate(data)
        return validated.root
    except ValidationError as e:
        return None, e