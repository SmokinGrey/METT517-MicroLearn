from sqlalchemy.orm import Session
import json

from . import models, schemas, auth

# --- User CRUD ---

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = auth.pwd_context.hash(user.password)
    db_user = models.User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# --- LearningMaterial CRUD ---

def get_materials_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.LearningMaterial).filter(models.LearningMaterial.owner_id == user_id).offset(skip).limit(limit).all()

def get_material(db: Session, material_id: int, user_id: int):
    return db.query(models.LearningMaterial).filter(models.LearningMaterial.id == material_id, models.LearningMaterial.owner_id == user_id).first()


def create_learning_material(db: Session, material: schemas.LearningMaterialCreate, user_id: int):
    # Create the main material entry
    db_material = models.LearningMaterial(
        summary=material.summary, 
        owner_id=user_id,
        mindmap=material.mindmap # 마인드맵 데이터 추가
    )
    db.add(db_material)
    db.commit()
    db.refresh(db_material)

    # Create related items
    for topic in material.key_topics:
        db_topic = models.KeyTopic(topic=topic, material_id=db_material.id)
        db.add(db_topic)
    
    for quiz_item in material.quiz:
        db_quiz = models.QuizItem(
            question=quiz_item.question,
            options=json.dumps(quiz_item.options), # list to JSON string
            answer=quiz_item.answer,
            material_id=db_material.id
        )
        db.add(db_quiz)

    for flashcard_item in material.flashcards:
        db_flashcard = models.Flashcard(
            term=flashcard_item.term,
            definition=flashcard_item.definition,
            material_id=db_material.id
        )
        db.add(db_flashcard)
    
    db.commit()
    db.refresh(db_material) # Refresh to load all related items
    return db_material
