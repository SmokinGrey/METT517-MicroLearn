from pydantic import BaseModel, Field
from typing import Optional, List


# --- MicroLearn Core Models ---

class QuizItem(BaseModel):
    question: str
    options: List[str]
    answer: str

class FlashcardItem(BaseModel):
    term: str
    definition: str

class LearningMaterial(BaseModel):
    summary: str
    key_topics: List[str]
    quiz: List[QuizItem]
    flashcards: List[FlashcardItem]

class SourceText(BaseModel):
    text: str


# --- Auth Models ---

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int

    class Config:
        orm_mode = True
