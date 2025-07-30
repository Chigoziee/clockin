import httpx
import os
from fastapi import HTTPException
import base64
from core.config import settings


class FaceAPI:
    def __init__(self):
        self.api_key = settings.FACE_API_KEY
        self.api_secret = settings.FACE_API_SECRET
        self.detect_url ="https://api-us.faceplusplus.com/facepp/v3/detect"
        self.compare_url = "https://api-us.faceplusplus.com/facepp/v3/compare"
        

    async def detect_face(self, image_data: str):
        payload = {
            "api_key": self.api_key,
            "api_secret": self.api_secret,
            "image_base64": image_data}
        
        async with httpx.AsyncClient(timeout=600, verify=False) as client:
            response = await client.post(self.detect_url, data=payload)

        if response.status_code == 200:
            num_faces = response.json().get("face_num", 0)
            if num_faces == 0:
                raise HTTPException(status_code=400, detail="No face detected in the image")
            elif num_faces > 1:
                raise HTTPException(status_code=400, detail="Multiple faces detected in the image")
            return True
        if response.status_code == 413:
            raise HTTPException(status_code=413, detail="Image file is larger than 2MB")

        raise HTTPException(status_code=response.status_code, detail="Facial detection failed")
    

    async def compare_face(self, image_data: str, image_url: str):
        if not image_url:
            raise HTTPException(status_code=400, detail="User has no image for reference")
        async with httpx.AsyncClient(timeout=600, verify=False) as client:
            respon = await client.get(image_url)
        if respon.status_code != 200:
            raise HTTPException(status_code=respon.status_code, detail="User image is invalid or inaccessible")
        
        user_image_data = base64.b64encode(respon.content).decode('utf-8')

        payload = {
                "api_key": self.api_key,
                "api_secret": self.api_secret,
                "image_base64_1": user_image_data,
                'image_base64_2': image_data,}    

        async with httpx.AsyncClient(timeout=600, verify=False) as client:
            response = await client.post(self.compare_url, data=payload)    
        
        if response.status_code == 200:
            confidence = response.json().get("confidence", 0)
            if confidence < 80:
                raise HTTPException(status_code=400, detail="Face does not match")
            return True
        if response.status_code == 413:
            raise HTTPException(status_code=413, detail="Image file is larger than 2MB")
        
        raise HTTPException(status_code=response.status_code, detail="Facial detection failed")
        
