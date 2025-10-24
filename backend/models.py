from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    notes = relationship("LearningNote", back_populates="owner")


class LearningNote(Base):
    __tablename__ = "learning_notes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="notes")
    sources = relationship("Source", back_populates="note", cascade="all, delete-orphan")
    material = relationship("LearningMaterial", uselist=False, back_populates="note", cascade="all, delete-orphan")


class Source(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, nullable=False)  # 'file', 'url'
    path = Column(String, nullable=False)
    content = Column(Text, nullable=True) # 요약 or 미리보기
    note_id = Column(Integer, ForeignKey("learning_notes.id"))

    note = relationship("LearningNote", back_populates="sources")


class LearningMaterial(Base):
    __tablename__ = "learning_materials"

    id = Column(Integer, primary_key=True, index=True)
    summary = Column(Text, nullable=False)
    mindmap = Column(JSON, nullable=True)
    audio_url = Column(String, nullable=True)
    note_id = Column(Integer, ForeignKey("learning_notes.id"))

    note = relationship("LearningNote", back_populates="material")
    key_topics = relationship("KeyTopic", back_populates="material", cascade="all, delete-orphan")
    quiz_items = relationship("QuizItem", back_populates="material", cascade="all, delete-orphan")
    flashcards = relationship("Flashcard", back_populates="material", cascade="all, delete-orphan")


class KeyTopic(Base):
    __tablename__ = "key_topics"

    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String, nullable=False)
    material_id = Column(Integer, ForeignKey("learning_materials.id"))

    material = relationship("LearningMaterial", back_populates="key_topics")


class QuizItem(Base):
    __tablename__ = "quiz_items"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    options = Column(String, nullable=False)  # JSON string
    answer = Column(String, nullable=False)
    material_id = Column(Integer, ForeignKey("learning_materials.id"))

    material = relationship("LearningMaterial", back_populates="quiz_items")


class Flashcard(Base):
    __tablename__ = "flashcards"

    id = Column(Integer, primary_key=True, index=True)
    term = Column(String, nullable=False)
    definition = Column(Text, nullable=False)
    material_id = Column(Integer, ForeignKey("learning_materials.id"))

    material = relationship("LearningMaterial", back_populates="flashcards")
