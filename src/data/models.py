from datetime import datetime, timezone
from pydantic import BaseModel, EmailStr, Field


class Admins(BaseModel):
    firstName: str
    lastName: str
    email: EmailStr
    username: str
    password: str
    organization: str
    verified: bool = False
    createdAt: datetime

class SignupRequest(BaseModel):
    firstName: str
    lastName: str
    email: EmailStr
    password: str
    organization: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class Users(BaseModel):
    image_url: str = None
    createdAt: datetime 
    email: EmailStr
    firstName: str
    lastName: str
    designation: str
    organization: str
    attendance: list = Field(default_factory=list)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class EmailRequest(BaseModel):
    email: EmailStr

class PasswordChange(BaseModel):
    token: str
    new_password: str