from fastapi import APIRouter, HTTPException, status, Form, UploadFile, File
from db import users_collection
from utils import hash_password, verify_password, create_access_token
from models import User
import base64

import datetime, random

user_router = APIRouter(prefix="/<username>", tags=["Actions"])


@user_router.post("/register")
async def register(
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    image: UploadFile = File(...)):
    user_exists = await users_collection.find_one({"email": email})
    if user_exists:
        raise HTTPException(status_code=400, detail="User already exists")
    img_read = await image.read()
    image_data = base64.b64encode(img_read).decode('utf-8')
    detect_url = "https://api-us.faceplusplus.com/facepp/v3/detect"
    detect_payload = {  "api_key": "sftNBQLl_QHFXoNRE53wAaZmmqe4eyBr",
                        "api_secret": "rho67OddK6r_dAp4AXxC56kyRdFn9c0M",
                        "image_base64": image_data}