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

# --- LearningNote CRUD ---

def create_learning_note(db: Session, note: schemas.LearningNoteCreate, user_id: int):
    db_note = models.LearningNote(**note.dict(), owner_id=user_id)
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note

def get_notes_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.LearningNote).filter(models.LearningNote.owner_id == user_id).offset(skip).limit(limit).all()

def get_note(db: Session, note_id: int, user_id: int):
    return db.query(models.LearningNote).filter(models.LearningNote.id == note_id, models.LearningNote.owner_id == user_id).first()

def delete_note(db: Session, note_id: int, user_id: int):
    db_note = get_note(db, note_id, user_id)
    if db_note:
        db.delete(db_note)
        db.commit()
        return True
    return False

# --- Source CRUD ---

def create_note_source(db: Session, source: schemas.SourceCreate, note_id: int):
    db_source = models.Source(**source.dict(), note_id=note_id)
    db.add(db_source)
    db.commit()
    db.refresh(db_source)
    return db_source


# --- LearningMaterial CRUD ---

def get_materials_by_note(db: Session, note_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.LearningMaterial).filter(models.LearningMaterial.note_id == note_id).offset(skip).limit(limit).all()

def get_material(db: Session, material_id: int, user_id: int):
    # 이제 material은 note에 속하므로, note를 통해 권한을 확인해야 합니다.
    # 이 함수는 로직 변경이 필요합니다. 우선은 note기반으로 변경합니다.
    return db.query(models.LearningMaterial).join(models.LearningNote).filter(
        models.LearningMaterial.id == material_id,
        models.LearningNote.owner_id == user_id
    ).first()


def create_learning_material(db: Session, material: schemas.LearningMaterialCreate, note_id: int):
    # Create the main material entry
    db_material = models.LearningMaterial(
        summary=material.summary, 
        note_id=note_id,
        mindmap=material.mindmap, # 마인드맵 데이터 추가
        audio_url=material.audio_url # 오디오 URL 데이터 추가
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
