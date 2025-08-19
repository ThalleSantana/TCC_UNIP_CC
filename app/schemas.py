from pydantic import BaseModel, EmailStr, HttpUrl
from typing import Optional, List

class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class AnalyzeRequest(BaseModel):
    platform: str
    url: HttpUrl

class CommentOut(BaseModel):
    author: Optional[str]
    text: str
    label: str
    score: int

    class Config:
        from_attributes = True

class AnalysisOut(BaseModel):
    id: int
    platform: str
    url: str
    status: str
    summary_positive: int
    summary_negative: int
    summary_neutral: int
    comments: List[CommentOut]

    class Config:
        from_attributes = True
