from fastapi import APIRouter, HTTPException
from db import admin_collection
from utils import email_verification, password_reset 
from security import hash_password, verify_password, create_access_token, decode_access_token, get_current_user
from models import Admins, SignupRequest, LoginRequest, TokenResponse, EmailRequest, PasswordChange
import random
from datetime import datetime, timezone


admin_router = APIRouter(prefix="/admin", tags=["Users"])


@admin_router.post("/signup")
async def signup(payload: SignupRequest):
    user_exists = await admin_collection.find_one({"email": payload.email})
    if user_exists:
        raise HTTPException(status_code=400, detail="Admin with email already exists")

    username = (payload.firstName[0] + payload.lastName).lower() + str(random.randint(100, 999))

    # Check if username already exists
    username_check = await admin_collection.find_one({"username": username})
    while username_check:
        username = (payload.firstName[0] + payload.lastName).lower() + str(random.randint(100, 999))
        username_check = admin_collection.find_one({"username": username})

    # Create new Admin 
    admin = Admins(
        firstName=payload.firstName.strip().title(),
        lastName=payload.lastName.strip().title(),
        email=payload.email,
        password=hash_password(payload.password),
        organization=payload.organization.strip().title(),
        username=username,
        createdAt=datetime.now(timezone.utc)
    )
    await admin_collection.insert_one(admin.model_dump()) 
    email_verification(payload.email, payload.firstName)

    return {"message": "User created successfully, Verification email sent"}


@admin_router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest):
    admin = await admin_collection.find_one({"email": payload.email})
    if not admin:
        raise HTTPException(status_code=404, detail="User not found")

    if not verify_password(payload.password, admin["password"]):
        raise HTTPException(status_code=401, detail="Invalid password")

    token = create_access_token({"sub": str(admin["username"]), "email": admin["email"]})
    return TokenResponse(access_token=token)


@admin_router.get("/verify-email")
async def verify_email(token: str):
    token_data = decode_access_token(token)
    email = token_data.get("sub")
    if email is None:
        raise HTTPException(status_code=400, detail="Invalid token")
    if datetime.fromtimestamp(token_data.get("exp"), tz=timezone.utc) < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Token has expired")
    # Update user in DB to verified
    await admin_collection.update_one(
        {"email": email}, {"$set": {"verified": True}})
    
    return {"message": "Email verified successfully!"}


@admin_router.post("/forget-password")
async def forget_password(request: EmailRequest):
    try:
        email = request.email
        user = await admin_collection.find_one({"email": email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        await password_reset(email)
        return {"message": "Password reset link sent to your email."}
        
    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred. Please try again later.")


@admin_router.get("/reset-password-token")
async def reset_password(token: str):
    token_data = decode_access_token(token)
    email = token_data.get("sub")
    if email is None:
        raise HTTPException(status_code=400, detail="Invalid token")
    if datetime.fromtimestamp(token_data.get("exp"), tz=timezone.utc) < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Token has expired")
    
    return {"message": "Token is valid", "email": email}

@admin_router.post("/change-password")
async def change_password(payload: PasswordChange):
    token_data = decode_access_token(payload.token)
    email = token_data.get("sub")
    if email is None:
        raise HTTPException(status_code=400, detail="Invalid token")
    if datetime.fromtimestamp(token_data.get("exp"), tz=timezone.utc) < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Token has expired")

    hashed_password = hash_password(payload.new_password)
    await admin_collection.update_one({"email": email}, {"$set": {"password": hashed_password}})
    
    return {"message": "Password changed successfully"}
    