from fastapi import FastAPI, HTTPException, File, UploadFile
from pydantic import BaseModel
from passlib.context import CryptContext
from typing import List
import io

# PDF 및 DOCX 처리를 위한 라이브러리 임포트
import docx
from pypdf2 import PdfReader

app = FastAPI()

# --- 기존 코드 ---

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# In-memory user "database"
fake_users_db = []

# Pydantic models for User Management
class UserCreate(BaseModel):
    username: str
    password: str

class UserInDB(BaseModel):
    username: str
    hashed_password: str

# --- AI 기능 모델 ---

class TextToSummarize(BaseModel):
    text: str

class SummaryResponse(BaseModel):
    summary: str


# --- API 엔드포인트 ---

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/register/", response_model=UserInDB)
def register_user(user: UserCreate):
    for existing_user in fake_users_db:
        if existing_user["username"] == user.username:
            raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = pwd_context.hash(user.password)
    user_in_db = {"username": user.username, "hashed_password": hashed_password}
    fake_users_db.append(user_in_db)
    return user_in_db

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
