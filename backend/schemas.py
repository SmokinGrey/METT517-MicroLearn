from pydantic import BaseModel, Field
from typing import Optional, List, Any


# --- Source Models ---

class SourceBase(BaseModel):
    type: str
    path: str
    content: Optional[str] = None

class SourceCreate(SourceBase):
    pass

class Source(SourceBase):
    id: int
    note_id: int

    class Config:
        orm_mode = True


# --- Learning Note Models ---

class LearningNoteBase(BaseModel):
    title: str

class LearningNoteCreate(LearningNoteBase):
    pass

class LearningNote(LearningNoteBase):
    id: int
    owner_id: int
    sources: List[Source] = []
    # material: Optional['LearningMaterial'] = None # 순환 참조 방지를 위해 주석 처리 또는 ForwardRef 사용

    class Config:
        orm_mode = True


# --- MicroLearn Core Models ---

# Base models for creation
class QuizItemBase(BaseModel):
    question: str
    options: List[str]
    answer: str

class FlashcardItemBase(BaseModel):
    term: str
    definition: str

class LearningMaterialCreate(BaseModel):
    summary: str
    key_topics: List[str]
    quiz: List[QuizItemBase]
    flashcards: List[FlashcardItemBase]
    mindmap: Optional[Any] = None
    audio_url: Optional[str] = None

class SourceText(BaseModel):
    text: str

# Models for reading from DB (includes ID, etc.)
class QuizItem(QuizItemBase):
    id: int
    material_id: int
    class Config:
        orm_mode = True

class FlashcardItem(FlashcardItemBase):
    id: int
    material_id: int
    class Config:
        orm_mode = True

class KeyTopic(BaseModel):
    id: int
    topic: str
    material_id: int
    class Config:
        orm_mode = True

class LearningMaterial(BaseModel):
    id: int
    summary: str
    note_id: int
    key_topics: List[KeyTopic] = []
    quiz_items: List[QuizItem] = []
    flashcards: List[FlashcardItem] = []
    mindmap: Optional[Any] = None
    audio_url: Optional[str] = None
    class Config:
        orm_mode = True

# 순환 참조 해결
LearningNote.update_forward_refs(LearningMaterial=LearningMaterial)


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
    notes: List[LearningNote] = []

    class Config:
        orm_mode = True
