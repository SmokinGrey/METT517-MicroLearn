from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    materials = relationship("LearningMaterial", back_populates="owner")


class LearningMaterial(Base):
    __tablename__ = "learning_materials"

    id = Column(Integer, primary_key=True, index=True)
    summary = Column(Text, nullable=False)
    mindmap = Column(JSON, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="materials")
    key_topics = relationship("KeyTopic", back_populates="material")
    quiz_items = relationship("QuizItem", back_populates="material")
    flashcards = relationship("Flashcard", back_populates="material")


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
