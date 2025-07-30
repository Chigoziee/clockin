from urllib.parse import urlparse
import cloudinary
import cloudinary.uploader
import asyncio
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

def extract_public_id(image_url: str) -> str:
    path = urlparse(image_url).path
    parts = path.split('/')
    public_id = '/'.join(parts[parts.index('upload') + 2:])
    return public_id.rsplit('.', 1)[0]

async def delete_cd_image(image_url: str):
    try:
        await asyncio.to_thread(cloudinary.uploader.destroy, extract_public_id(image_url))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete image: {str(e)}") from e
