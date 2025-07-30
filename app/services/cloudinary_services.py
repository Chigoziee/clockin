from urllib.parse import urlparse
import cloudinary
import cloudinary.uploader
import os
import asyncio
from dotenv import load_dotenv
from fastapi import HTTPException  
from core.config import settings


cloudinary.config( 
    cloud_name = settings.CLOUDINARY_CLOUD_NAME,
    api_key = settings.CLOUDINARY_API_KEY,
    api_secret = settings.CLOUDINARY_API_SECRET,
    secure=True)

async def cd_upload(file):
    result = await asyncio.to_thread(cloudinary.uploader.upload, file)
    return result['secure_url']

async def delete_cd_image(image_url: str):
    path = urlparse(image_url).path
    parts = path.split('/')
    public_id = '/'.join(parts[parts.index('upload') + 2:])
    public_id = public_id.rsplit('.', 1)[0] 
    try:
        await asyncio.to_thread(cloudinary.uploader.destroy, public_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete image: {str(e)}") from e

