from fastapi import APIRouter, HTTPException, status, Form, UploadFile, File
from db import users_collection
from utils import cd_upload
from models import User
import base64
from face import FaceAPI
from datetime import datetime, timezone


user_router = APIRouter(prefix="/user", tags=["Actions"])

face = FaceAPI()

@user_router.post("/{username}/register")
async def register(payload: User, image: UploadFile = File(...)):
    user_exists = await users_collection.find_one({"email": payload.email})
    if user_exists:
        raise HTTPException(status_code=400, detail="User already exists")
    
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid image format") 
       
    img_read = await image.read()
    image_file_size = len(img_read)
    if image_file_size > 2 * 1024 * 1024:  # 2MB limit
        raise HTTPException(status_code=400, detail="Image file is larger than 2MB")
    image_data = base64.b64encode(img_read).decode('utf-8')
    detect_face = await face.detect_face(image_data)       
    if detect_face:
        image_url = cd_upload(img_read)
        user_data = {
            "email": payload.email,
            "firstName": payload.firstName,
            "lastName": payload.lastName,
            "designation": payload.designation,
            "image_url": image_url,
            "createdAt": datetime.now(timezone.utc),
            "updatedAt": datetime.now(timezone.utc)
        }
        await users_collection.insert_one(user_data)
        return {"message": "User registered successfully"}
    
    

