from fastapi import APIRouter, HTTPException, status, Form, UploadFile, File, Depends
from db.mongo import users_collection
from services.cloudinary_services import cd_upload, delete_cd_image
from api.deps import get_current_user
from core.utils import is_token_expired, get_verified_admin, attendance_log_limiter as atll
from models.user import Users
import base64
from services.facial_recognition import FaceAPI
from datetime import datetime, timedelta, timezone


user_router = APIRouter(prefix="/{admin_username}", tags=["Users"])
face = FaceAPI()

@user_router.get("/users")
async def get_users(admin_username: str, current_user: dict = Depends(get_current_user)):

    if current_user.get("sub") != admin_username:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized action")
    if is_token_expired(current_user):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Please login again to continue")
    
    admin_exists = await get_verified_admin(admin_username)
    
    users = await users_collection.find({"organization": admin_exists["organization"]}).to_list()
    if not users:
        return {"message": "No users found"}
    
    users = [{i:v for i, v in user.items() if i in ["firstName", "lastName", "email", "designation", "image_url"]} for user in users]

    return {"users": users,
            "organization": admin_exists["organization"],
            "User Count": len(users)}


@user_router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    admin_username: str,
    firstName: str = Form(...),
    lastName: str = Form(...),
    email: str = Form(...),
    designation: str = Form(...),
    image: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    if current_user.get("sub") != admin_username:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized action")
    if is_token_expired(current_user):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Please login again to continue")
    
    admin_exists =  await get_verified_admin(admin_username)
    
    if await users_collection.find_one({"email": email.strip().lower()}):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")
    
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="Invalid image format") 
       
    img_read = await image.read()
    image_file_size = len(img_read)

    if image_file_size > 2 * 1024 * 1024:  # 2MB limit
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Image file is larger than 2MB")
    image_data = base64.b64encode(img_read).decode('utf-8')
    detect_face = await face.detect_face(image_data)       
    if detect_face:
        image_url = await cd_upload(img_read)
        user_data = Users(
            email=email.strip().lower(),
            firstName=firstName.strip().title(),
            lastName=lastName.strip().title(),
            designation=designation.strip().title(),
            image_url=image_url,
            createdAt=datetime.now(timezone.utc),
            organization=admin_exists['organization'])
                            
        await users_collection.insert_one(user_data.model_dump())
        return {"message": "User registered successfully"}
    
    
@user_router.delete("/delete/{user_email}")
async def signin_user(admin_username: str, user_email: str, current_user: dict = Depends(get_current_user)):
    if current_user.get("sub") != admin_username:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized action")
    if is_token_expired(current_user):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Please login again to continue")
    
    user = await users_collection.find_one({"email": user_email.strip()})
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    await delete_cd_image(user['image_url'])
    await users_collection.delete_one({"email": user_email.strip()})
    return {"message": "User deleted successfully"}


@user_router.post("/signin/{user_email}")
async def delete_user(
    admin_username: str, 
    user_email: str, 
    image: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
    ):
    if current_user.get("sub") != admin_username:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized action")
    if is_token_expired(current_user):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Please login to continue")
    
    user_exists = await users_collection.find_one({"email": user_email.strip()})
    if not user_exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="Invalid image format")
    img_read = await image.read()
    image_file_size = len(img_read)     
    if image_file_size > 2 * 1024 * 1024:  # 2MB limit
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Image file is larger than 2MB")    
    image_data = base64.b64encode(img_read).decode('utf-8')
    
    await face.compare_face(image_data, user_exists.get("image_url", ""))
    current_time = datetime.now(timezone.utc) + timedelta(hours=1)
    current_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
    attendance_logs = user_exists.get("attendance", [])
    if len(attendance_logs) > 0:
         # If the last log is from today, do not allow another sign-in
        last_signin = datetime.strptime(attendance_logs[-1], "%Y-%m-%d %H:%M:%S").date()
        if last_signin == datetime.now(timezone.utc).date():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{user_exists['firstName']} {user_exists['lastName']} already signed in for today")

    attendance_logs = atll(attendance_logs, current_time)
    
    await users_collection.update_one({"email": user_exists["email"]}, {"$set": {"attendance": attendance_logs}})
    
    return {"message": f"{user_exists['firstName']} {user_exists['lastName']} signed in successfully"}
