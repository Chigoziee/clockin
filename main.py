import os
import time
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse, JSONResponse
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient


load_dotenv()
app = FastAPI()
client = AsyncIOMotorClient(os.environ["CONNECTION_STRING"])
db = client["clockinDB"]
collection = db["admin"]

print(list(collection.find_one({"email": "sk.hyginus@gmail.com"})))

# lastName="Ifenji"
# firstName="chigozie"
# createdAt = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
# print(firstName[0].capitalize()+lastName.lower()+createdAt[-4:].replace(":",""))

# @app.get("/")
# def homepage():
#     return {"message": "Clockin API is live 🌍!!!"}
#
# @app.post("/auth/signup")
# async def create_admin(
#         firstName: str = Form(...),
#         lastName: str = Form(...),
#         email: str = Form(...),
#         organization: str = Form(...),
#         password: str = Form(...),
# ):
#     createdAt = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
#     await collection.insert_one({"firstName": firstName.strip(),
#                                  "lastName":lastName.strip(),
#                                  "email": email.strip(),
#                                  "organization": organization.strip(),
#                                  "password": password.strip(),
#                                  "verified": False,
#                                  "createdAt": createdAt,
#                                  "username": firstName[0].capitalize()+lastName.lower()+createdAt[-4:].replace(":","")})
#
# @app.post("/auth/login")
# async def create_admin(
#         email: str = Form(...),
#         password: str = Form(...)
# ):
