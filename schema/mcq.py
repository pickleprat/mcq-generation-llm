from pydantic import BaseModel, RootModel, field_validator
from typing import List, Literal

class MCQOptions(BaseModel):
    A: str
    B: str
    C: str
    D: str
    E: str


class MCQ(BaseModel):
    answer: Literal["A", "B", "C", "D", "E"]
    options: MCQOptions
    question: str
    reasoning: str
    mcq_number: int
    topics_covered: List[str]

    @field_validator("topics_covered")
    @classmethod
    def topics_not_empty(cls, v):
        if not v:
            raise ValueError("topics_covered must not be empty")
        return v


class MCQList(RootModel[List[MCQ]]):
    pass