from fastapi import APIRouter, HTTPException, status
from db import admin_collection
from utils import hash_password, verify_password, create_access_token, decode_access_token, email_verification
from models import Admins, SignupRequest, LoginRequest, TokenResponse
from bson import ObjectId
import random
from datetime import datetime, timezone

user_router = APIRouter(prefix="/users", tags=["Users"])


@user_router.post("/signup")
async def signup(payload: SignupRequest):
    user_exists = await admin_collection.find_one({"email": payload.email})
    if user_exists:
        raise HTTPException(status_code=400, detail="Admin with email already exists")

    username = (payload.firstName[0] + payload.lastName).lower()+ str(random.randint(100, 999))
    user = Admins(
        firstName=payload.firstName,
        lastName=payload.lastName,
        email=payload.email,
        password=hash_password(payload.password),
        organization=payload.organization,
        username=username
    )
    await admin_collection.insert_one(user.model_dump())
    email_verification(payload.email, payload.firstName)

    return {"message": "User created successfully, Verification email sent"}


@user_router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest):
    user = await admin_collection.find_one({"email": payload.email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not verify_password(payload.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid password")

    token = create_access_token({"sub": str(user["username"]), "email": user["email"]})
    return TokenResponse(access_token=token)



@user_router.get("/verify-email")
async def verify_email(token: str):
    token_data = decode_access_token(token)
    email = token_data.get("sub")
    if email is None:
        raise HTTPException(status_code=400, detail="Invalid token")
    if datetime.fromtimestamp(token_data.get("exp"), tz=timezone.utc) < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Token has expired")
    # Update user in DB to verified
    await admin_collection.update_one(
        {"email": email}, {"$set": {"verified": True}}
    )
    return {"message": "Email verified successfully!"}