from fastapi import Depends, FastAPI, HTTPException, File, UploadFile, status, Form
from fastapi.responses import StreamingResponse
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
import os
import json
from typing import List, Optional
from dotenv import load_dotenv
import google.generativeai as genai

from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
import io

# PDF 및 DOCX 처리를 위한 라이브러리 임포트
import docx
from pypdf import PdfReader # pypdf2 is deprecated, use pypdf
import trafilatura
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound
import re

from fastapi.staticfiles import StaticFiles
from pathlib import Path

from . import auth, crud, models, schemas, rag_handler, tts_handler
from .database import SessionLocal, engine

load_dotenv() # .env 파일에서 환경 변수 로드

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# 정적 파일(오디오 등) 제공을 위한 설정
app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")

# CORS 미들웨어 추가
origins = [
    "http://localhost:3000",  # React 개발 서버
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Auth Endpoints ---

@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, username=form_data.username)
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="사용자 이름 또는 비밀번호가 잘못되었습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="이미 등록된 사용자 이름입니다.")
    return crud.create_user(db=db, user=user)

@app.get("/users/me", response_model=schemas.User)
async def read_users_me(current_user: schemas.User = Depends(auth.get_current_user)):
    return current_user

# --- Learning Note Endpoints (New) ---

@app.post("/api/notes", response_model=schemas.LearningNote)
def create_learning_note(
    note: schemas.LearningNoteCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_user)
):
    """
    새로운 학습 노트를 생성합니다.
    """
    return crud.create_learning_note(db=db, note=note, user_id=current_user.id)

@app.get("/api/notes", response_model=List[schemas.LearningNote])
def read_user_notes(
    skip: int = 0, limit: int = 100,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_user)
):
    """
    현재 사용자의 모든 학습 노트를 조회합니다.
    """
    notes = crud.get_notes_by_user(db, user_id=current_user.id, skip=skip, limit=limit)
    return notes

@app.get("/api/notes/{note_id}", response_model=schemas.LearningNote)
def read_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_user)
):
    """
    특정 학습 노트를 조회합니다.
    """
    db_note = crud.get_note(db, note_id=note_id, user_id=current_user.id)
    if db_note is None:
        raise HTTPException(status_code=404, detail="노트를 찾을 수 없습니다.")
    return db_note

@app.delete("/api/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_user)
):
    """
    특정 학습 노트를 삭제합니다.
    """
    success = crud.delete_note(db, note_id=note_id, user_id=current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="노트를 찾을 수 없습니다.")
    return


# --- Source Endpoints (New) ---

@app.post("/api/notes/{note_id}/sources", response_model=schemas.Source)
async def add_source_to_note(
    note_id: int,
    file: Optional[UploadFile] = File(None),
    url: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_user)
):
    """
    학습 노트에 새로운 소스(파일 또는 URL)를 추가합니다.
    """
    db_note = crud.get_note(db, note_id=note_id, user_id=current_user.id)
    if db_note is None:
        raise HTTPException(status_code=404, detail="노트를 찾을 수 없습니다.")

    if file:
        # 파일 처리 로직 (Phase 3에서 구체화)
        # 우선 파일명과 타입만 저장
        source_create = schemas.SourceCreate(type='file', path=file.filename, content="")
        return crud.create_note_source(db=db, source=source_create, note_id=note_id)
    elif url:
        # URL 처리 로직 (Phase 3에서 구체화)
        source_create = schemas.SourceCreate(type='url', path=url, content="")
        return crud.create_note_source(db=db, source=source_create, note_id=note_id)
    else:
        raise HTTPException(status_code=400, detail="파일이나 URL이 제공되지 않았습니다.")


# --- Deprecated Material Endpoints ---

# @app.get("/api/my-materials", response_model=List[schemas.LearningMaterial])
# def read_my_materials(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
#     materials = crud.get_materials_by_user(db, user_id=current_user.id, skip=skip, limit=limit)
#     return materials

# @app.get("/api/materials/{material_id}", response_model=schemas.LearningMaterial)
# def read_material(material_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
#     db_material = crud.get_material(db, material_id=material_id, user_id=current_user.id)
#     if db_material is None:
#         raise HTTPException(status_code=404, detail="Material not found or you do not have permission to view it")
#     return db_material


# --- RAG Chat Endpoint (To be refactored for notes) ---

class ChatQuery(BaseModel):
    question: str

@app.post("/api/notes/{note_id}/chat")
async def chat_with_note(
    note_id: int,
    query: ChatQuery,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_user)
):
    """
    특정 학습 노트에 대한 채팅 질문을 스트리밍으로 처리합니다.
    """
    db_note = crud.get_note(db, note_id=note_id, user_id=current_user.id)
    if db_note is None:
        raise HTTPException(status_code=404, detail="노트를 찾을 수 없거나 접근 권한이 없습니다.")

    # RAG 핸들러는 이제 note_id를 기반으로 작동해야 합니다.
    return StreamingResponse(
        rag_handler.stream_rag_response_from_note(note_id=note_id, question=query.question),
        media_type="text/event-stream"
    )


# --- AI Material Generation (Refactored for Notes) ---

async def _generate_ai_materials(text: str, db: Session, note_id: int, source_path: str):
    """Helper function to generate learning materials and add text to the note's vector store."""
    api_key = os.getenv("GEMINI_API_KEY")

    # Vectorize and store the source text for RAG
    rag_handler.add_source_to_vector_store(note_id=note_id, source_text=text, source_path=source_path)

    # API 키가 없거나 임시 키일 경우 목업 데이터 반환
    if not api_key or api_key == "YOUR_API_KEY_HERE":
        print("Warning: GEMINI_API_KEY is not configured. Returning mock data.")
        mock_data = schemas.LearningMaterialCreate(
            summary=f"[목업 데이터] '{source_path}'의 내용을 요약한 결과입니다.",
            key_topics=["핵심 주제 1", "핵심 주제 2"],
            quiz=[schemas.QuizItemBase(question="첫 번째 질문입니다.", options=["A", "B", "C", "D"], answer="A")],
            flashcards=[schemas.FlashcardItemBase(term="용어 1", definition="설명 1")],
            mindmap={"name": "[목업] 중심 주제", "children": [{"name": "하위 주제 1"}]},
            audio_url=None
        )
        # For mock data, we don't create a full material, just return the structure
        # This part of the logic might need adjustment based on desired behavior for mock generation.
        # For now, we'll skip creating a material entry in the DB for mock data to avoid confusion.
        # A better approach would be to create a consolidated material for the note.
        # This is a placeholder for the real implementation of multi-source analysis.
        return mock_data # Returning the structure, not a DB object

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')

        prompt = f"""다음 텍스트를 분석하여 마이크로러닝 학습 자료를 생성해줘. 반드시 아래의 JSON 형식과 동일한 구조로 응답해야 해. 각 필드에 대한 설명은 다음과 같아.

- summary: 텍스트의 핵심 내용을 요약한 문단.
- key_topics: 텍스트의 핵심 주제나 키워드를 담은 문자열 배열.
- quiz: 텍스트의 내용을 바탕으로 한 객관식 퀴즈 2개. options는 4개의 선택지를 포함해야 하고, answer는 그 중 정답 텍스트여야 해.
- flashcards: 텍스트에 등장하는 중요 용어와 그 설명을 담은 용어 카드 2개.
- mindmap: 텍스트의 핵심 개념들을 계층적으로 구조화한 마인드맵 데이터. 'name'과 'children' 키를 사용하는 중첩된(nested) JSON 객체 형식이어야 해. 최상위 객체는 하나여야 해.

**분석할 텍스트:**
{text}

**JSON 출력 형식:**
{{
  "summary": "<요약 내용>",
  "key_topics": ["<주제1>", "<주제2>", ...],
  "quiz": [
    {{
      "question": "<질문1>",
      "options": ["<선택지1>", "<선택지2>", "<선택지3>", "<선택지4>"],
      "answer": "<정답>"
    }},
    {{
      "question": "<질문2>",
      "options": ["<선택지1>", "<선택지2>", "<선택지3>", "<선택지4>"],
      "answer": "<정답>"
    }}
  ],
  "flashcards": [
    {{
      "term": "<용어1>",
      "definition": "<설명1>"
    }},
    {{
      "term": "<용어2>",
      "definition": "<설명2>"
    }}
  ],
  "mindmap": {{
    "name": "<중심 주제>",
    "children": [
      {{
        "name": "<하위 주제 1>",
        "children": [
          {{ "name": "<세부 주제 1-1>" }},
          {{ "name": "<세부 주제 1-2>" }}
        ]
      }},
      {{ "name": "<하위 주제 2>" }}
    ]
  }}
}}
"""

        response = await model.generate_content_async(prompt)
        cleaned_response_text = response.text.strip().replace('```json', '').replace('```', '')
        response_json = json.loads(cleaned_response_text)

        if isinstance(response_json.get("mindmap"), str):
            try:
                response_json["mindmap"] = json.loads(response_json["mindmap"])
            except json.JSONDecodeError:
                response_json["mindmap"] = None
        
        validated_material = schemas.LearningMaterialCreate(**response_json)

        audio_url = None
        if validated_material.summary:
            audio_url = tts_handler.create_audio_briefing(validated_material.summary)
        validated_material.audio_url = audio_url
        
        # This part needs to be re-evaluated. Instead of creating a new material for each source,
        # we should have one consolidated material per note. 
        # For now, we will continue to create one to maintain some functionality.
        db_material = crud.create_learning_material(db=db, material=validated_material, note_id=note_id)

        return db_material

    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="AI 자료 생성 중 오류가 발생했습니다.")

@app.post("/api/notes/{note_id}/generate-from-file", response_model=schemas.LearningMaterial)
async def generate_materials_from_file(
    note_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_user)
):
    db_note = crud.get_note(db, note_id=note_id, user_id=current_user.id)
    if db_note is None:
        raise HTTPException(status_code=404, detail="노트를 찾을 수 없습니다.")

    filename = file.filename
    if not (filename.endswith(".txt") or filename.endswith(".pdf") or filename.endswith(".docx")):
        raise HTTPException(status_code=400, detail="지원하지 않는 파일 형식입니다.")

    extracted_text = ""
    try:
        contents = await file.read()
        if filename.endswith(".txt"): extracted_text = contents.decode("utf-8")
        elif filename.endswith(".pdf"): 
            with io.BytesIO(contents) as f:
                reader = PdfReader(f)
                for page in reader.pages: extracted_text += page.extract_text() or ""
        elif filename.endswith(".docx"): 
            with io.BytesIO(contents) as f:
                doc = docx.Document(f)
                for para in doc.paragraphs: extracted_text += para.text + "\n"
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"파일 처리 실패: {str(e)}")

    if not extracted_text.strip():
        raise HTTPException(status_code=400, detail="파일에서 텍스트를 추출할 수 없습니다.")

    # 소스 정보도 DB에 저장
    source_create = schemas.SourceCreate(type='file', path=filename, content=extracted_text[:500]) # 미리보기
    crud.create_note_source(db=db, source=source_create, note_id=note_id)

    return await _generate_ai_materials(text=extracted_text, db=db, note_id=note_id, source_path=filename)

@app.post("/api/notes/{note_id}/generate-from-text", response_model=schemas.LearningMaterial)
async def generate_materials_from_text(
    note_id: int,
    source_text: schemas.SourceText,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_user)
):
    db_note = crud.get_note(db, note_id=note_id, user_id=current_user.id)
    if db_note is None:
        raise HTTPException(status_code=404, detail="노트를 찾을 수 없습니다.")

    # 소스 정보도 DB에 저장
    source_create = schemas.SourceCreate(type='text', path='text_input', content=source_text.text[:500])
    crud.create_note_source(db=db, source=source_create, note_id=note_id)

    return await _generate_ai_materials(text=source_text.text, db=db, note_id=note_id, source_path='text_input')


# --- New Endpoints for URL & YouTube (Refactored for Notes) ---

class UrlSource(BaseModel):
    url: str

def get_youtube_video_id(url: str):
    regex = r"(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})"
    match = re.search(regex, url)
    return match.group(1) if match else None

@app.post("/api/notes/{note_id}/generate-from-url", response_model=schemas.LearningMaterial)
async def generate_materials_from_url(
    note_id: int,
    source: UrlSource,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_user)
):
    db_note = crud.get_note(db, note_id=note_id, user_id=current_user.id)
    if db_note is None: raise HTTPException(status_code=404, detail="노트를 찾을 수 없습니다.")
    
    try:
        downloaded = trafilatura.fetch_url(source.url)
        if downloaded is None: raise HTTPException(status_code=400, detail="URL에서 콘텐츠를 가져올 수 없습니다.")
        extracted_text = trafilatura.extract(downloaded)
        if not extracted_text or not extracted_text.strip(): raise HTTPException(status_code=400, detail="URL에서 텍스트를 추출할 수 없습니다.")

        source_create = schemas.SourceCreate(type='url', path=source.url, content=extracted_text[:500])
        crud.create_note_source(db=db, source=source_create, note_id=note_id)

        return await _generate_ai_materials(text=extracted_text, db=db, note_id=note_id, source_path=source.url)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"URL 처리 중 오류 발생: {str(e)}")

@app.post("/api/notes/{note_id}/generate-from-youtube", response_model=schemas.LearningMaterial)
async def generate_materials_from_youtube(
    note_id: int,
    source: UrlSource,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_user)
):
    db_note = crud.get_note(db, note_id=note_id, user_id=current_user.id)
    if db_note is None: raise HTTPException(status_code=404, detail="노트를 찾을 수 없습니다.")

    try:
        video_id = get_youtube_video_id(source.url)
        if not video_id: raise HTTPException(status_code=400, detail="유효하지 않은 YouTube URL입니다.")

        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['ko', 'en'])
        extracted_text = " ".join([item['text'] for item in transcript_list])
        if not extracted_text.strip(): raise HTTPException(status_code=400, detail="자막을 추출할 수 없습니다.")

        source_create = schemas.SourceCreate(type='youtube', path=source.url, content=extracted_text[:500])
        crud.create_note_source(db=db, source=source_create, note_id=note_id)

        return await _generate_ai_materials(text=extracted_text, db=db, note_id=note_id, source_path=source.url)
    
    except NoTranscriptFound:
        raise HTTPException(status_code=404, detail="해당 영상에 분석 가능한 한국어 또는 영어 자막이 존재하지 않습니다.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"YouTube 처리 중 오류 발생: {str(e)}")



@app.get("/users/", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    return db_user


@app.get("/")
def read_root():
    return {"Hello": "World"}
