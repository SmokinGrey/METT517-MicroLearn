from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from passlib.context import CryptContext
from typing import List

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

# --- 신규 추가: AI 기능 모델 ---

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
    # Check if user already exists
    for existing_user in fake_users_db:
        if existing_user["username"] == user.username:
            raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = pwd_context.hash(user.password)
    user_in_db = {"username": user.username, "hashed_password": hashed_password}
    fake_users_db.append(user_in_db)
    return user_in_db

# --- 신규 추가: AI 기능 엔드포인트 ---

@app.post("/api/summarize", response_model=SummaryResponse)
async def summarize_text(payload: TextToSummarize):
    """
    입력된 텍스트를 요약합니다.
    MVP 단계에서는 실제 AI 대신 간단한 로직으로 대체합니다.
    """
    input_text = payload.text
    if not input_text or not input_text.strip():
        raise HTTPException(status_code=400, detail="Text to summarize cannot be empty.")

    # TODO: 여기에 실제 AI API (OpenAI, Gemini 등) 호출 로직을 구현합니다.
    # 예: summary = await call_ai_summary_api(input_text)
    
    # 임시 요약 로직 (처음 100자 + '...')
    summary = f"[임시 요약] {input_text[:100]}..."

    return SummaryResponse(summary=summary)