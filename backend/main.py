from fastapi import Depends, FastAPI, HTTPException, File, UploadFile, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
import os
import json
from dotenv import load_dotenv
import google.generativeai as genai

from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
import io

# PDF 및 DOCX 처리를 위한 라이브러리 임포트
import docx
from pypdf2 import PdfReader

from . import auth, crud, models, schemas
from .database import SessionLocal, engine

load_dotenv() # .env 파일에서 환경 변수 로드

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

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

# --- API 엔드포인트 ---

@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, username=form_data.username)
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
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
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db=db, user=user)

@app.get("/users/me", response_model=schemas.User)
async def read_users_me(current_user: schemas.User = Depends(auth.get_current_user)):
    return current_user

@app.get("/api/my-materials", response_model=List[schemas.LearningMaterial])
def read_my_materials(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    """
    현재 로그인된 사용자가 생성한 모든 학습 자료 목록을 반환합니다.
    """
    materials = crud.get_materials_by_user(db, user_id=current_user.id, skip=skip, limit=limit)
    return materials

@app.post("/api/generate-materials-from-file", response_model=schemas.LearningMaterial)
async def generate_materials_from_file(file: UploadFile = File(...), db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    """
    업로드된 파일(.txt, .pdf, .docx)에서 텍스트를 추출하고 통합 학습 자료를 생성합니다. (로그인 필요)
    """
    filename = file.filename
    if not (filename.endswith(".txt") or filename.endswith(".pdf") or filename.endswith(".docx")):
        raise HTTPException(status_code=400, detail="Unsupported file type. Please upload .txt, .pdf, or .docx files.")

    extracted_text = ""
    try:
        contents = await file.read()
        
        if filename.endswith(".txt"):
            extracted_text = contents.decode("utf-8")
        
        elif filename.endswith(".pdf"):
            with io.BytesIO(contents) as f:
                reader = PdfReader(f)
                for page in reader.pages:
                    extracted_text += page.extract_text() or ""
        
        elif filename.endswith(".docx"):
            with io.BytesIO(contents) as f:
                doc = docx.Document(f)
                for para in doc.paragraphs:
                    extracted_text += para.text + "\n"

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process file: {str(e)}")

    if not extracted_text or not extracted_text.strip():
        raise HTTPException(status_code=400, detail="Could not extract text from the file or the file is empty.")

    # TODO: 이 추출된 텍스트(extracted_text)를 실제 AI 호출 로직에 전달해야 합니다.
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "YOUR_API_KEY_HERE":
        mock_data = schemas.LearningMaterialCreate(
            summary="[파일 기반 목업 데이터] 이것은 AI가 생성한 목업 요약입니다.",
            key_topics=["파일 주제 1", "파일 주제 2"],
            quiz=[schemas.QuizItemBase(question="파일 기반 질문입니다. 정답은?", options=["A", "B"], answer="A")],
            flashcards=[schemas.FlashcardItemBase(term="파일 용어", definition="파일 용어에 대한 설명입니다.")]
        )
        return crud.create_learning_material(db=db, material=mock_data, user_id=current_user.id)
    
    raise HTTPException(status_code=501, detail="AI integration for file upload is not implemented yet.")


@app.post("/api/generate-materials", response_model=schemas.LearningMaterial)
async def generate_materials(source_text: schemas.SourceText, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    """
    입력된 텍스트를 기반으로 통합 학습 자료를 생성합니다. (로그인 필요)
    """
    api_key = os.getenv("GEMINI_API_KEY")

    # API 키가 없거나 임시 키일 경우 목업 데이터 반환
    if not api_key or api_key == "YOUR_API_KEY_HERE":
        print("Warning: GEMINI_API_KEY is not configured. Returning mock data.")
        mock_data = schemas.LearningMaterialCreate(
            summary="[목업 데이터] 이것은 AI가 생성한 목업 요약입니다. 원본 텍스트의 핵심 내용을 담고 있습니다.",
            key_topics=["핵심 주제 1", "핵심 주제 2", "중요 컨셉 3"],
            quiz=[
                schemas.QuizItemBase(question="첫 번째 질문입니다. 정답은 무엇일까요?", options=["A", "B", "C", "D"], answer="A"),
                schemas.QuizItemBase(question="두 번째 질문입니다. 이 개념을 설명하세요.", options=["보기1", "보기2", "보기3", "보기4"], answer="보기2"),
            ],
            flashcards=[
                schemas.FlashcardItemBase(term="용어 1", definition="용어 1에 대한 설명입니다."),
                schemas.FlashcardItemBase(term="용어 2", definition="용어 2에 대한 상세한 설명입니다."),
            ]
        )
        return crud.create_learning_material(db=db, material=mock_data, user_id=current_user.id)

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')

        prompt = f"""다음 텍스트를 분석하여 마이크로러닝 학습 자료를 생성해줘. 반드시 아래의 JSON 형식과 동일한 구조로 응답해야 해. 각 필드에 대한 설명은 다음과 같아.

- summary: 텍스트의 핵심 내용을 요약한 문단.
- key_topics: 텍스트의 핵심 주제나 키워드를 담은 문자열 배열.
- quiz: 텍스트의 내용을 바탕으로 한 객관식 퀴즈 2개. options는 4개의 선택지를 포함해야 하고, answer는 그 중 정답 텍스트여야 해.
- flashcards: 텍스트에 등장하는 중요 용어와 그 설명을 담은 용어 카드 2개.

**분석할 텍스트:**
{source_text.text}

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
  ]
}}
"""

        response = await model.generate_content_async(prompt)
        
        # 응답 텍스트에서 JSON 부분만 추출
        cleaned_response_text = response.text.strip().replace('```json', '').replace('```', '')
        
        # JSON 파싱
        response_json = json.loads(cleaned_response_text)
        
        # 스키마를 사용하여 데이터 유효성 검사 및 변환
        validated_material = schemas.LearningMaterialCreate(**response_json)
        
        # 데이터베이스에 저장
        return crud.create_learning_material(db=db, material=validated_material, user_id=current_user.id)

    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="AI 자료 생성 중 오류가 발생했습니다.")


@app.get("/users/", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/api/summarize", response_model=SummaryResponse)
async def summarize_text(payload: TextToSummarize):
    """
    입력된 텍스트를 요약합니다.
    """
    input_text = payload.text
    if not input_text or not input_text.strip():
        raise HTTPException(status_code=400, detail="Text to summarize cannot be empty.")

    # TODO: 여기에 실제 AI API 호출 로직을 구현합니다.
    summary = f"[임시 요약] {input_text[:100]}..."
    return SummaryResponse(summary=summary)

# --- 신규 추가: 파일 업로드 및 요약 엔드포인트 ---

@app.post("/api/upload-and-summarize", response_model=SummaryResponse)
async def upload_and_summarize_file(file: UploadFile = File(...)):
    """
    업로드된 파일(.txt, .pdf, .docx)에서 텍스트를 추출하고 요약합니다.
    """
    filename = file.filename
    if not (filename.endswith(".txt") or filename.endswith(".pdf") or filename.endswith(".docx")):
        raise HTTPException(status_code=400, detail="Unsupported file type. Please upload .txt, .pdf, or .docx files.")

    extracted_text = ""
    try:
        contents = await file.read()
        
        if filename.endswith(".txt"):
            extracted_text = contents.decode("utf-8")
        
        elif filename.endswith(".pdf"):
            with io.BytesIO(contents) as f:
                reader = PdfReader(f)
                for page in reader.pages:
                    extracted_text += page.extract_text() or ""
        
        elif filename.endswith(".docx"):
            with io.BytesIO(contents) as f:
                doc = docx.Document(f)
                for para in doc.paragraphs:
                    extracted_text += para.text + "\n"

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process file: {str(e)}")

    if not extracted_text or not extracted_text.strip():
        raise HTTPException(status_code=400, detail="Could not extract text from the file or the file is empty.")

    # 기존의 임시 요약 로직 재사용
    # TODO: 여기에 실제 AI API 호출 로직을 구현합니다.
    summary = f"[파일 요약] {extracted_text[:100]}..."
    return SummaryResponse(summary=summary)
