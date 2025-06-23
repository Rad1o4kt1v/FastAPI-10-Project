from pydantic import BaseModel
from typing import List

class PollCreate(BaseModel):
    question: str
    options: List[str]

class Poll(BaseModel):
    id: int
    question: str
    options: List[str]
    votes: List[int] 