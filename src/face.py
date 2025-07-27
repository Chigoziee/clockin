import httpx
from dotenv import load_dotenv
import os

load_dotenv()


class FaceAPI:
    def __init__(self):
        self.api_key = os.getenv("FACE_API_KEY")
        self.api_secret = os.getenv("FACE_API_SECRET")
        self.detect_url ="https://api-us.faceplusplus.com/facepp/v3/detect"
        

    async def detect_face(self, image_data: str):
        payload = {
            "api_key": self.api_key,
            "api_secret": self.api_secret,
            "image_base64": image_data}
        
        async with httpx.AsyncClient(timeout=600, verify=False) as client:
            response = await client.get(self.detect_url)

        if response.status_code == 200:
            num_faces = response.json().get("face_num", 0)
            if num_faces == 0:
                raise Exception("No face detected in the image")
            elif num_faces > 1:
                raise Exception("Multiple face detected in the image")
            return True
        if response.status_code == 413:
            raise Exception("Image file is too large")
        if response.status_code == 400:
            raise Exception("Invalid image format")
