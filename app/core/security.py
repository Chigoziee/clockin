from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta, timezone
from core.config import settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
JWT_SECRET = settings.JWT_SECRET
JWT_ALGORITHM = settings.JWT_ALGORITHM

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict, hours=24):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(hours=hours)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.JWTError:
        return None

