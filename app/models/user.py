from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

class Users(BaseModel):
    image_url: str = None
    createdAt: datetime 
    email: EmailStr
    firstName: str
    lastName: str
    designation: str
    organization: str
    attendance: list = Field(default_factory=list)
