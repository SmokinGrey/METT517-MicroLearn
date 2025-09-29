from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from passlib.context import CryptContext
from typing import List

app = FastAPI()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# In-memory user "database"
fake_users_db = []

# Pydantic models
class UserCreate(BaseModel):
    username: str
    password: str

class UserInDB(BaseModel):
    username: str
    hashed_password: str

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
