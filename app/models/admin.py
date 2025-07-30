from datetime import datetime
from pydantic import BaseModel, EmailStr

class Admins(BaseModel):
    firstName: str
    lastName: str
    email: EmailStr
    username: str
    password: str
    organization: str
    verified: bool = False
    createdAt: datetime
