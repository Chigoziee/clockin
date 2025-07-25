# app/models.py
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class Admins(BaseModel):
    firstName: str
    lastName: str
    email: EmailStr
    username: str
    password: str
    organization: str
    verified: bool = False
    createdAt: datetime = Field(default_factory=datetime.utcnow)

class SignupRequest(BaseModel):
    firstName: str
    lastName: str
    email: EmailStr
    password: str
    organization: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"